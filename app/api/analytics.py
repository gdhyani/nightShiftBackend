from fastapi import APIRouter, Depends
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models import Trade

router = APIRouter(tags=["analytics"])


@router.get("/api/analytics/performance")
async def get_performance(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(
            func.count(Trade.id).label("total_trades"),
            func.sum(
                case((Trade.pnl > 0, 1), else_=0)
            ).label("wins"),
            func.sum(
                case((Trade.pnl <= 0, 1), else_=0)
            ).label("losses"),
            func.coalesce(func.sum(Trade.pnl), 0.0).label("total_pnl"),
        ).where(Trade.status == "closed")
    )
    row = result.one()
    total = row.total_trades or 0
    wins = row.wins or 0
    losses = row.losses or 0
    return {
        "total_trades": total,
        "wins": wins,
        "losses": losses,
        "win_rate": round(wins / total, 4) if total > 0 else 0.0,
        "total_pnl": round(float(row.total_pnl), 2),
    }


@router.get("/api/analytics/equity-curve")
async def get_equity_curve(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Trade.closed_at, Trade.pnl)
        .where(Trade.status == "closed")
        .where(Trade.pnl.isnot(None))
        .order_by(Trade.closed_at.asc())
    )
    trades = result.all()

    curve = []
    balance = 10000.0
    for closed_at, pnl in trades:
        balance += pnl
        curve.append({
            "time": closed_at.isoformat() if closed_at else None,
            "balance": round(balance, 2),
        })
    return curve


@router.get("/api/analytics/per-strategy")
async def get_per_strategy_analytics(
    session: AsyncSession = Depends(get_session),
):
    from sqlalchemy import case as sql_case
    result = await session.execute(
        select(
            Trade.strategy_id,
            func.count().label("total"),
            func.sum(sql_case((Trade.pnl > 0, 1), else_=0)).label("wins"),
            func.sum(Trade.pnl).label("pnl"),
        )
        .where(Trade.status == "closed")
        .group_by(Trade.strategy_id)
    )
    return [
        {"strategy_id": r.strategy_id, "total_trades": r.total,
         "wins": r.wins or 0, "losses": r.total - (r.wins or 0),
         "pnl": round(float(r.pnl or 0), 5)}
        for r in result.all()
    ]


@router.get("/api/analytics/per-symbol")
async def get_per_symbol_analytics(
    session: AsyncSession = Depends(get_session),
):
    from sqlalchemy import case as sql_case
    result = await session.execute(
        select(
            Trade.symbol,
            func.count().label("total"),
            func.sum(sql_case((Trade.pnl > 0, 1), else_=0)).label("wins"),
            func.sum(Trade.pnl).label("pnl"),
        )
        .where(Trade.status == "closed")
        .group_by(Trade.symbol)
    )
    return [
        {"symbol": r.symbol, "total_trades": r.total,
         "wins": r.wins or 0, "losses": r.total - (r.wins or 0),
         "pnl": round(float(r.pnl or 0), 5)}
        for r in result.all()
    ]


@router.get("/api/analytics/daily-pnl")
async def get_daily_pnl(
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(
            func.date(Trade.closed_at).label("date"),
            func.sum(Trade.pnl).label("pnl"),
            func.count().label("trades_count"),
        )
        .where(Trade.status == "closed", Trade.closed_at.isnot(None))
        .group_by(func.date(Trade.closed_at))
        .order_by(func.date(Trade.closed_at))
    )
    return [
        {"date": str(r.date), "pnl": round(float(r.pnl or 0), 5),
         "trades_count": r.trades_count}
        for r in result.all()
    ]
