from datetime import datetime, timezone

import pytest

from app.models import Indicator


@pytest.fixture
async def seeded_indicators(db_session):
    base = datetime(2026, 3, 30, 10, 0, 0, tzinfo=timezone.utc)
    for i in range(5):
        for name in ["sma_20", "rsi_14", "ema_9"]:
            db_session.add(Indicator(
                symbol="EUR_USD",
                timeframe="H1",
                timestamp=base.replace(hour=10 + i),
                name=name,
                value=50.0 + i + (0.1 if name == "rsi_14" else 0),
            ))
    await db_session.commit()


async def test_get_indicators_returns_list(client, seeded_indicators):
    response = await client.get("/api/indicators/EUR_USD/H1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 15


async def test_get_indicators_filter_by_names(client, seeded_indicators):
    response = await client.get("/api/indicators/EUR_USD/H1?names=sma_20,rsi_14")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10
    names = {d["name"] for d in data}
    assert names == {"sma_20", "rsi_14"}


async def test_get_indicators_empty(client):
    response = await client.get("/api/indicators/UNKNOWN/H1")
    assert response.status_code == 200
    assert response.json() == []
