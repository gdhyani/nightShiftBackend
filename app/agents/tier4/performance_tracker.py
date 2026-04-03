from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Trade

AGENT_NAME = "performance_tracker"


async def run(session: AsyncSession) -> dict:
    """Pure computation — no LLM needed. Queries trade stats from DB."""
    result = await session.execute(
        select(
            func.count(Trade.id).label("total_trades"),
            func.sum(case((Trade.pnl > 0, 1), else_=0)).label("wins"),
            func.sum(case((Trade.pnl <= 0, 1), else_=0)).label("losses"),
            func.coalesce(func.sum(Trade.pnl), 0.0).label("total_pnl"),
            func.coalesce(func.avg(Trade.pnl), 0.0).label("avg_pnl"),
            func.coalesce(func.max(Trade.pnl), 0.0).label("best_trade"),
            func.coalesce(func.min(Trade.pnl), 0.0).label("worst_trade"),
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
        "avg_pnl": round(float(row.avg_pnl), 2),
        "best_trade": round(float(row.best_trade), 2),
        "worst_trade": round(float(row.worst_trade), 2),
    }
