from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models import Indicator, IndicatorSchema

router = APIRouter(prefix="/api/indicators", tags=["indicators"])


@router.get("/{symbol}/{timeframe}", response_model=list[IndicatorSchema])
async def get_indicators(
    symbol: str,
    timeframe: str,
    names: str | None = Query(None, description="Comma-separated indicator names"),
    limit: int = 500,
    session: AsyncSession = Depends(get_session),
):
    query = (
        select(Indicator)
        .where(Indicator.symbol == symbol, Indicator.timeframe == timeframe)
    )
    if names:
        name_list = [n.strip() for n in names.split(",")]
        query = query.where(Indicator.name.in_(name_list))
    query = query.order_by(Indicator.timestamp.asc()).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()
