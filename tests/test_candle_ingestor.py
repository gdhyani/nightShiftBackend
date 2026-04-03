from datetime import datetime, timezone

import pytest
from sqlalchemy import func, select

from app.models import Candle
from app.services.candle_ingestor import CandleIngestor

MOCK_CANDLES = [
    {
        "symbol": "NSE_EQ|INE848E01016",
        "timeframe": "60",
        "timestamp": datetime(2026, 3, 30, 10, 0, 0, tzinfo=timezone.utc),
        "open": 2450.0, "high": 2465.0, "low": 2445.0, "close": 2460.0, "volume": 100000,
    },
    {
        "symbol": "NSE_EQ|INE848E01016",
        "timeframe": "60",
        "timestamp": datetime(2026, 3, 30, 11, 0, 0, tzinfo=timezone.utc),
        "open": 2460.0, "high": 2470.0, "low": 2455.0, "close": 2468.0, "volume": 120000,
    },
]


async def test_ingest_candles_inserts(db_session):
    ingestor = CandleIngestor()
    inserted = await ingestor.ingest_candles(db_session, MOCK_CANDLES)
    assert inserted == 2
    result = await db_session.execute(
        select(Candle).where(Candle.symbol == "NSE_EQ|INE848E01016")
    )
    assert len(result.scalars().all()) == 2


async def test_ingest_candles_handles_duplicates(db_session):
    ingestor = CandleIngestor()
    await ingestor.ingest_candles(db_session, MOCK_CANDLES)
    inserted = await ingestor.ingest_candles(db_session, MOCK_CANDLES)
    assert inserted == 0
    result = await db_session.execute(
        select(func.count()).select_from(Candle)
        .where(Candle.symbol == "NSE_EQ|INE848E01016")
    )
    assert result.scalar() == 2
