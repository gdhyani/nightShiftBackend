from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.oanda import OandaService


@pytest.fixture
def oanda_service():
    return OandaService(
        api_key="test-key",
        account_id="test-account",
        api_url="https://api-fxpractice.oanda.com",
    )


MOCK_CANDLES_RESPONSE = {
    "instrument": "EUR_USD",
    "granularity": "H1",
    "candles": [
        {
            "complete": True,
            "volume": 1000,
            "time": "2026-03-30T10:00:00.000000000Z",
            "mid": {"o": "1.08000", "h": "1.08500", "l": "1.07800", "c": "1.08400"},
        },
        {
            "complete": True,
            "volume": 1200,
            "time": "2026-03-30T11:00:00.000000000Z",
            "mid": {"o": "1.08400", "h": "1.08700", "l": "1.08200", "c": "1.08600"},
        },
    ],
}


async def test_fetch_candles_returns_parsed_list(oanda_service):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = MOCK_CANDLES_RESPONSE
    mock_response.raise_for_status = MagicMock()

    with patch.object(oanda_service._client, "get", new=AsyncMock(return_value=mock_response)):
        candles = await oanda_service.fetch_candles("EUR_USD", "H1", count=2)

    assert len(candles) == 2
    assert candles[0]["symbol"] == "EUR_USD"
    assert candles[0]["timeframe"] == "H1"
    assert candles[0]["open"] == 1.08000
    assert candles[0]["high"] == 1.08500
    assert candles[0]["close"] == 1.08400
    assert candles[0]["volume"] == 1000
    assert isinstance(candles[0]["timestamp"], datetime)


async def test_fetch_candles_filters_incomplete(oanda_service):
    response_data = {
        "instrument": "EUR_USD",
        "granularity": "H1",
        "candles": [
            {
                "complete": True,
                "volume": 100,
                "time": "2026-03-30T10:00:00.000000000Z",
                "mid": {"o": "1.08", "h": "1.085", "l": "1.078", "c": "1.084"},
            },
            {
                "complete": False,
                "volume": 50,
                "time": "2026-03-30T11:00:00.000000000Z",
                "mid": {"o": "1.084", "h": "1.087", "l": "1.082", "c": "1.086"},
            },
        ],
    }
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = response_data
    mock_response.raise_for_status = MagicMock()

    with patch.object(oanda_service._client, "get", new=AsyncMock(return_value=mock_response)):
        candles = await oanda_service.fetch_candles("EUR_USD", "H1", count=2)

    assert len(candles) == 1
    assert candles[0]["open"] == 1.08


async def test_granularity_mapping(oanda_service):
    assert oanda_service._map_timeframe("1m") == "M1"
    assert oanda_service._map_timeframe("5m") == "M5"
    assert oanda_service._map_timeframe("15m") == "M15"
    assert oanda_service._map_timeframe("1h") == "H1"
    assert oanda_service._map_timeframe("4h") == "H4"
    assert oanda_service._map_timeframe("1D") == "D"
    assert oanda_service._map_timeframe("H1") == "H1"
