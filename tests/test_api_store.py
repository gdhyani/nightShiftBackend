from datetime import datetime, timezone

import pytest

from app.models import StoreSnapshot


@pytest.fixture
async def seeded_snapshot(db_session):
    snapshot = StoreSnapshot(
        symbol="EUR_USD",
        data={
            "sma_20": 1.0870,
            "ema_9": 1.0885,
            "rsi_14": 55.3,
            "vwap": 1.0865,
        },
        updated_at=datetime(2026, 3, 30, 14, 0, 0, tzinfo=timezone.utc),
    )
    db_session.add(snapshot)
    await db_session.commit()


async def test_get_store_snapshot(client, seeded_snapshot):
    response = await client.get("/api/store/EUR_USD")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "EUR_USD"
    assert data["data"]["rsi_14"] == 55.3
    assert data["data"]["vwap"] == 1.0865


async def test_get_store_snapshot_not_found(client):
    response = await client.get("/api/store/UNKNOWN")
    assert response.status_code == 404
