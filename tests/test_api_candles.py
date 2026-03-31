from datetime import datetime, timezone

import pytest

from app.models import Candle


@pytest.fixture
async def seeded_candles(db_session):
    base = datetime(2026, 3, 30, 10, 0, 0, tzinfo=timezone.utc)
    for i in range(5):
        candle = Candle(
            symbol="EUR_USD",
            timeframe="H1",
            timestamp=base.replace(hour=10 + i),
            open=1.08 + i * 0.002,
            high=1.085 + i * 0.002,
            low=1.078 + i * 0.002,
            close=1.084 + i * 0.002,
            volume=1000 + i * 100,
        )
        db_session.add(candle)
    await db_session.commit()


async def test_get_candles_returns_list(client, seeded_candles):
    response = await client.get("/api/candles/EUR_USD/H1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5


async def test_get_candles_empty_symbol(client):
    response = await client.get("/api/candles/UNKNOWN/H1")
    assert response.status_code == 200
    assert response.json() == []


async def test_get_candles_with_limit(client, seeded_candles):
    response = await client.get("/api/candles/EUR_USD/H1", params={"limit": 2})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
