from datetime import datetime, timezone
import pytest
from app.models import Trade


@pytest.fixture
async def seeded_analytics_trades(db_session):
    trades = [
        (1, "NSE_EQ|INE848E01016", "BUY", 0.5, "2026-04-01"),
        (1, "NSE_EQ|INE848E01016", "BUY", -0.3, "2026-04-01"),
        (2, "NSE_EQ|INE040A01034", "SELL", 0.8, "2026-04-02"),
    ]
    for sid, sym, direction, pnl, date_str in trades:
        db_session.add(Trade(
            strategy_id=sid, symbol=sym, direction=direction,
            entry_price=2500.0, stop_loss=2450.0, take_profit=2600.0,
            quantity=10.0, status="closed", pnl=pnl, source="paper",
            closed_at=datetime.fromisoformat(f"{date_str}T14:00:00+00:00"),
        ))
    await db_session.commit()


async def test_per_strategy(client, seeded_analytics_trades):
    resp = await client.get("/api/analytics/per-strategy")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


async def test_per_symbol(client, seeded_analytics_trades):
    resp = await client.get("/api/analytics/per-symbol")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


async def test_daily_pnl(client, seeded_analytics_trades):
    resp = await client.get("/api/analytics/daily-pnl")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1
