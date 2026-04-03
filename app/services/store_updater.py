import logging
from datetime import datetime, timezone

import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Candle, StoreSnapshot
from app.services.store_calculator import StoreCalculator

logger = logging.getLogger(__name__)


class StoreUpdater:
    def __init__(self, calculator: StoreCalculator):
        self._calculator = calculator

    async def update_snapshot(
        self, session: AsyncSession, symbol: str, timeframe: str, limit: int = 200
    ) -> dict | None:
        result = await session.execute(
            select(Candle)
            .where(Candle.symbol == symbol, Candle.timeframe == timeframe)
            .order_by(Candle.timestamp.desc())
            .limit(limit)
        )
        candles = list(reversed(result.scalars().all()))

        if len(candles) < 20:
            logger.warning(f"Not enough candles for {symbol}/{timeframe}: {len(candles)}")
            return None

        df = pd.DataFrame([{
            "open": c.open, "high": c.high, "low": c.low,
            "close": c.close, "volume": c.volume,
        } for c in candles])

        indicators = self._calculator.calculate_all(df)

        existing = await session.execute(
            select(StoreSnapshot).where(StoreSnapshot.symbol == symbol)
        )
        snapshot = existing.scalar_one_or_none()

        if snapshot is None:
            snapshot = StoreSnapshot(
                symbol=symbol,
                data={timeframe: indicators},
                updated_at=datetime.now(timezone.utc),
            )
            session.add(snapshot)
        else:
            data = dict(snapshot.data) if snapshot.data else {}
            data[timeframe] = indicators
            snapshot.data = data
            snapshot.updated_at = datetime.now(timezone.utc)

        await session.commit()
        logger.info(f"Updated store snapshot for {symbol}/{timeframe}")
        return indicators
