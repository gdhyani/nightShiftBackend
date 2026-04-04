from datetime import datetime, timezone
import pytest
from app.models import Account, Position, Trade


@pytest.fixture
async def seeded_portfolio(db_session):
    db_session.add(Account(balance=1000000.0, equity=1000000.0))
    db_session.add(Trade(
        strategy_id=1, symbol="NSE_EQ|INE848E01016", direction="BUY",
        entry_price=2500.0, stop_loss=2450.0, take_profit=2600.0,
        quantity=10.0, status="open", source="paper",
        opened_at=datetime(2026, 4, 1, 10, 0, 0, tzinfo=timezone.utc),
    ))
    await db_session.flush()
    db_session.add(Position(
        trade_id=1, symbol="NSE_EQ|INE848E01016", direction="BUY",
        entry_price=2500.0, current_price=2520.0, stop_loss=2450.0,
        take_profit=2600.0, quantity=10.0, unrealized_pnl=200.0, status="open",
    ))
    await db_session.commit()


async def test_get_holdings(client, seeded_portfolio):
    resp = await client.get("/api/portfolio/holdings")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_get_positions(client, seeded_portfolio):
    resp = await client.get("/api/portfolio/positions")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["symbol"] == "NSE_EQ|INE848E01016"


async def test_get_margins(client, seeded_portfolio):
    resp = await client.get("/api/portfolio/margins")
    assert resp.status_code == 200
    assert resp.json()["balance"] == 1000000.0
