from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models import Candle, CandleSchema

router = APIRouter(prefix="/api/candles", tags=["candles"])


@router.get("/{symbol}/{timeframe}", response_model=list[CandleSchema])
async def get_candles(
    symbol: str,
    timeframe: str,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
):
    query = (
        select(Candle)
        .where(Candle.symbol == symbol, Candle.timeframe == timeframe)
        .order_by(Candle.timestamp.desc())
        .limit(limit)
    )
    result = await session.execute(query)
    candles = result.scalars().all()
    return list(reversed(candles))
