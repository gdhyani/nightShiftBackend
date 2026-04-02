from datetime import datetime, timezone

import pytest

from app.models import Strategy, StrategyRun


@pytest.fixture
async def seeded_strategy(db_session):
    strategy = Strategy(
        name="SMC Swing", symbols="EUR_USD,GBP_USD", enabled=True,
        schedule_interval=1800,
        pipeline_config={"stages": [{"name": "analyst"}, {"name": "evaluator"}]},
    )
    db_session.add(strategy)
    await db_session.flush()
    db_session.add(StrategyRun(
        strategy_id=strategy.id, symbol="EUR_USD",
        stages={"stages": [{"agent": "analyst", "output": {}}]},
        decision="WAIT",
    ))
    await db_session.commit()
    return strategy


async def test_list_strategies(client, seeded_strategy):
    response = await client.get("/api/strategies")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == "SMC Swing"


async def test_create_strategy(client):
    response = await client.post("/api/strategies", json={
        "name": "Test Strategy", "symbols": "EUR_USD",
        "pipeline_config": {"stages": [{"name": "analyst"}, {"name": "evaluator"}]},
    })
    assert response.status_code == 200
    assert response.json()["name"] == "Test Strategy"


async def test_get_strategy(client, seeded_strategy):
    response = await client.get(f"/api/strategies/{seeded_strategy.id}")
    assert response.status_code == 200
    assert response.json()["name"] == "SMC Swing"


async def test_patch_strategy_toggle(client, seeded_strategy):
    response = await client.patch(f"/api/strategies/{seeded_strategy.id}", json={"enabled": False})
    assert response.status_code == 200
    assert response.json()["enabled"] is False


async def test_get_strategy_runs(client, seeded_strategy):
    response = await client.get(f"/api/strategies/{seeded_strategy.id}/runs")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["decision"] == "WAIT"
