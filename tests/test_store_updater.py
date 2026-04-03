from datetime import datetime, timezone

import pytest
from sqlalchemy import select, func

from app.models import Candle, StoreSnapshot
from app.services.store_calculator import StoreCalculator
from app.services.store_updater import StoreUpdater


@pytest.fixture
async def seeded_candles_for_update(db_session):
    base_price = 1.0800
    for i in range(50):
        day = 28 + i // 24
        hour = i % 24
        candle = Candle(
            symbol="EUR_USD",
            timeframe="H1",
            timestamp=datetime(2026, 3, day, hour, 0, 0, tzinfo=timezone.utc),
            open=base_price + i * 0.0005 - 0.0002,
            high=base_price + i * 0.0005 + 0.003,
            low=base_price + i * 0.0005 - 0.003,
            close=base_price + i * 0.0005,
            volume=1000 + i * 10,
        )
        db_session.add(candle)
    await db_session.commit()


async def test_update_snapshot_creates_entry(db_session, seeded_candles_for_update):
    updater = StoreUpdater(calculator=StoreCalculator())
    await updater.update_snapshot(db_session, "EUR_USD", "H1")
    result = await db_session.execute(
        select(StoreSnapshot).where(StoreSnapshot.symbol == "EUR_USD")
    )
    snapshot = result.scalar_one()
    assert "H1" in snapshot.data
    assert "rsi_14" in snapshot.data["H1"]
    assert "macd_line" in snapshot.data["H1"]
    assert "bb_upper" in snapshot.data["H1"]
    assert "atr_14" in snapshot.data["H1"]


async def test_update_snapshot_updates_existing(db_session, seeded_candles_for_update):
    updater = StoreUpdater(calculator=StoreCalculator())
    await updater.update_snapshot(db_session, "EUR_USD", "H1")
    await updater.update_snapshot(db_session, "EUR_USD", "H1")
    result = await db_session.execute(
        select(func.count()).select_from(StoreSnapshot).where(StoreSnapshot.symbol == "EUR_USD")
    )
    assert result.scalar() == 1
