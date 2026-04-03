from datetime import datetime, timezone

import pytest
from httpx import AsyncClient

from app.models import Trade


@pytest.fixture
async def seeded_trades(db_session):
    """Seed 3 closed trades with known P&L."""
    trades = [
        Trade(
            symbol="EUR_USD",
            direction="long",
            entry_price=1.0800,
            exit_price=1.0850,
            stop_loss=1.0750,
            take_profit=1.0900,
            quantity=1.0,
            status="closed",
            pnl=50.0,
            closed_at=datetime(2026, 3, 30, 12, 0, tzinfo=timezone.utc),
        ),
        Trade(
            symbol="EUR_USD",
            direction="short",
            entry_price=1.0850,
            exit_price=1.0870,
            stop_loss=1.0900,
            take_profit=1.0800,
            quantity=1.0,
            status="closed",
            pnl=-20.0,
            closed_at=datetime(2026, 3, 30, 14, 0, tzinfo=timezone.utc),
        ),
        Trade(
            symbol="GBP_USD",
            direction="long",
            entry_price=1.2600,
            exit_price=1.2650,
            stop_loss=1.2550,
            take_profit=1.2700,
            quantity=1.0,
            status="closed",
            pnl=50.0,
            closed_at=datetime(2026, 3, 30, 16, 0, tzinfo=timezone.utc),
        ),
    ]
    for t in trades:
        db_session.add(t)
    await db_session.flush()
    return trades


@pytest.mark.asyncio
async def test_performance_endpoint(client: AsyncClient, seeded_trades):
    resp = await client.get("/api/analytics/performance")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_trades"] == 3
    assert data["wins"] == 2
    assert data["losses"] == 1
    assert data["total_pnl"] == 80.0
    assert data["win_rate"] == round(2 / 3, 4)


@pytest.mark.asyncio
async def test_equity_curve_endpoint(client: AsyncClient, seeded_trades):
    resp = await client.get("/api/analytics/equity-curve")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 3
    # First point: 10000 + 50 = 10050
    assert data[0]["balance"] == 10050.0
    # Last point: 10000 + 50 - 20 + 50 = 10080
    assert data[-1]["balance"] == 10080.0


@pytest.mark.asyncio
async def test_performance_empty(client: AsyncClient):
    resp = await client.get("/api/analytics/performance")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_trades"] == 0
    assert data["win_rate"] == 0.0
