from datetime import datetime, timezone

import pytest
from sqlalchemy import select

from app.models import AgentInsight
from app.services.agent_runner import AgentRunner


async def test_save_insight(db_session):
    runner = AgentRunner(session_factory=None)
    await runner.save_insight(
        session=db_session,
        agent_name="test_agent",
        symbol="EUR_USD",
        insight_type="test",
        data={"key": "value"},
        confidence=0.85,
        ttl_minutes=30,
    )
    result = await db_session.execute(
        select(AgentInsight).where(AgentInsight.agent_name == "test_agent")
    )
    insight = result.scalar_one()
    assert insight.symbol == "EUR_USD"
    assert insight.data["key"] == "value"
    assert insight.confidence == 0.85
    assert insight.expires_at > insight.created_at
