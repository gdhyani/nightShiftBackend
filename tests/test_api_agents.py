from datetime import datetime, timezone, timedelta

import pytest

from app.models import AgentInsight


@pytest.fixture
async def seeded_agent_insights(db_session):
    now = datetime(2026, 3, 30, 14, 0, 0, tzinfo=timezone.utc)
    for agent, itype in [("news_agent", "news"), ("session_agent", "sessions")]:
        db_session.add(AgentInsight(
            agent_name=agent, symbol="EUR_USD", insight_type=itype,
            data={"test": True}, confidence=0.8,
            created_at=now, expires_at=now + timedelta(hours=1),
        ))
    await db_session.commit()


async def test_get_agents_list(client):
    response = await client.get("/api/agents")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 8
    names = {a["name"] for a in data}
    assert "news_agent" in names
    assert "bias_agent" in names


async def test_get_agent_insights(client, seeded_agent_insights):
    response = await client.get("/api/agents/insights?symbol=EUR_USD")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


async def test_get_agent_insights_filter(client, seeded_agent_insights):
    response = await client.get("/api/agents/insights?symbol=EUR_USD&agent_name=news_agent")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["agent_name"] == "news_agent"
