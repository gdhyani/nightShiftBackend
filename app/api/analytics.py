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
