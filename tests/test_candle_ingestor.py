from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
from sqlalchemy import select, func

from app.models import Candle
from app.services.candle_ingestor import CandleIngestor


MOCK_CANDLES = [
    {
        "symbol": "EUR_USD",
        "timeframe": "H1",
        "timestamp": datetime(2026, 3, 30, 10, 0, 0, tzinfo=timezone.utc),
        "open": 1.08, "high": 1.085, "low": 1.078, "close": 1.084, "volume": 1000,
    },
    {
        "symbol": "EUR_USD",
        "timeframe": "H1",
        "timestamp": datetime(2026, 3, 30, 11, 0, 0, tzinfo=timezone.utc),
        "open": 1.084, "high": 1.087, "low": 1.082, "close": 1.086, "volume": 1200,
    },
]


@pytest.fixture
def mock_oanda():
    service = AsyncMock()
    service.fetch_candles = AsyncMock(return_value=MOCK_CANDLES)
    return service


async def test_ingest_once_inserts_candles(db_session, mock_oanda):
    ingestor = CandleIngestor(oanda=mock_oanda)
    count = await ingestor.ingest_once(db_session, "EUR_USD", "H1")
    assert count == 2
    result = await db_session.execute(select(Candle).where(Candle.symbol == "EUR_USD"))
    candles = result.scalars().all()
    assert len(candles) == 2


async def test_ingest_once_handles_duplicates(db_session, mock_oanda):
    ingestor = CandleIngestor(oanda=mock_oanda)
    await ingestor.ingest_once(db_session, "EUR_USD", "H1")
    count = await ingestor.ingest_once(db_session, "EUR_USD", "H1")
    assert count == 2
    result = await db_session.execute(
        select(func.count()).select_from(Candle).where(Candle.symbol == "EUR_USD")
    )
    assert result.scalar() == 2
