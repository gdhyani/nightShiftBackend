from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.upstox_ingestor import UpstoxIngestor


@pytest.fixture
def mock_upstox():
    svc = MagicMock()
    svc.get_historical_candles = AsyncMock(return_value=[
        {"symbol": "NSE_EQ|INE002A01018", "timeframe": "minutes_5", "timestamp": "2026-01-02T09:15:00", "open": 100, "high": 105, "low": 99, "close": 103, "volume": 5000},
        {"symbol": "NSE_EQ|INE002A01018", "timeframe": "minutes_5", "timestamp": "2026-01-02T09:20:00", "open": 103, "high": 106, "low": 102, "close": 105, "volume": 6000},
    ])
    return svc


@pytest.fixture
def mock_candle_ingestor():
    svc = MagicMock()
    svc.ingest_candles = AsyncMock(return_value=2)
    return svc


@pytest.fixture
def mock_store_updater():
    svc = MagicMock()
    svc.update_snapshot = AsyncMock(return_value={"sma_20": 100.0})
    return svc


async def test_ingest_symbol(mock_upstox, mock_candle_ingestor, mock_store_updater):
    ingestor = UpstoxIngestor(mock_upstox, mock_candle_ingestor, mock_store_updater)
    session = AsyncMock()

    count = await ingestor.ingest_symbol(
        session=session,
        symbol="NSE_EQ|INE002A01018",
        timeframe="5",
        token="test-token",
    )

    assert count == 2
    mock_upstox.get_historical_candles.assert_called_once()
    mock_candle_ingestor.ingest_candles.assert_called_once()
    mock_store_updater.update_snapshot.assert_called_once()


def test_map_timeframe():
    assert UpstoxIngestor.map_timeframe("1") == ("minutes", 1)
    assert UpstoxIngestor.map_timeframe("5") == ("minutes", 5)
    assert UpstoxIngestor.map_timeframe("15") == ("minutes", 15)
    assert UpstoxIngestor.map_timeframe("60") == ("minutes", 60)
    assert UpstoxIngestor.map_timeframe("day") == ("days", 1)
    assert UpstoxIngestor.map_timeframe("30") == ("minutes", 30)
