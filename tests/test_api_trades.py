from datetime import datetime, timezone

import pytest

from app.models import Trade, Position


@pytest.fixture
async def seeded_trades(db_session):
    for i, status in enumerate(["open", "closed", "closed"]):
        trade = Trade(
            strategy_id=1, symbol="EUR_USD", direction="BUY",
            entry_price=1.08 + i * 0.002, stop_loss=1.078,
            take_profit=1.09, quantity=0.1, status=status,
            pnl=0.005 if status == "closed" else None,
            reasoning={"test": True},
            opened_at=datetime(2026, 3, 30, 10 + i, 0, 0, tzinfo=timezone.utc),
        )
        db_session.add(trade)
    await db_session.flush()
    db_session.add(Position(
        trade_id=1, symbol="EUR_USD", direction="BUY",
        entry_price=1.08, current_price=1.08,
        stop_loss=1.078, take_profit=1.09,
        quantity=0.1, status="open",
    ))
    await db_session.commit()


async def test_list_trades(client, seeded_trades):
    response = await client.get("/api/trades")
    assert response.status_code == 200
    assert len(response.json()) == 3


async def test_list_trades_filter_status(client, seeded_trades):
    response = await client.get("/api/trades?status=open")
    assert response.status_code == 200
    assert len(response.json()) == 1


async def test_get_trade(client, seeded_trades):
    response = await client.get("/api/trades/1")
    assert response.status_code == 200
    assert response.json()["symbol"] == "EUR_USD"


async def test_get_positions(client, seeded_trades):
    response = await client.get("/api/positions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["status"] == "open"
