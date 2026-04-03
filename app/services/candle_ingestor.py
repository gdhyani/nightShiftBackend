import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Candle

logger = logging.getLogger(__name__)


class CandleIngestor:
    async def ingest_candles(
        self, session: AsyncSession, candles: list[dict]
    ) -> int:
        inserted = 0
        for c in candles:
            existing = await session.execute(
                select(Candle).where(
                    Candle.symbol == c["symbol"],
                    Candle.timeframe == c["timeframe"],
                    Candle.timestamp == c["timestamp"],
                )
            )
            if existing.scalar_one_or_none() is not None:
                continue
            session.add(Candle(**c))
            inserted += 1
        await session.commit()
        return inserted
