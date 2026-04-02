from datetime import datetime, timezone, timedelta

import pytest

from app.agents.tools.market_data import read_candles, read_store
from app.agents.tools.insights import read_insights
from app.agents.tools.skills import read_skill
from app.agents.tools.session import get_session_info
from app.models import Candle, StoreSnapshot, AgentInsight


@pytest.fixture
async def seeded_data_for_tools(db_session):
    for i in range(5):
        db_session.add(Candle(
            symbol="EUR_USD", timeframe="H1",
            timestamp=datetime(2026, 3, 30, 10 + i, 0, 0, tzinfo=timezone.utc),
            open=1.08 + i * 0.001, high=1.085 + i * 0.001,
            low=1.078 + i * 0.001, close=1.084 + i * 0.001, volume=1000,
        ))
    db_session.add(StoreSnapshot(
        symbol="EUR_USD",
        data={"H1": {"rsi_14": 55.3, "sma_20": 1.085}},
        updated_at=datetime(2026, 3, 30, 14, 0, 0, tzinfo=timezone.utc),
    ))
    db_session.add(AgentInsight(
        agent_name="session_agent", symbol="EUR_USD", insight_type="sessions",
        data={"current_session": "london", "killzone_active": True},
        confidence=0.9,
        created_at=datetime(2026, 3, 30, 14, 0, 0, tzinfo=timezone.utc),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
    ))
    await db_session.commit()


async def test_read_candles(db_session, seeded_data_for_tools):
    result = await read_candles(db_session, "EUR_USD", "H1", 5)
    assert isinstance(result, str)
    assert "EUR_USD" in result
    assert "1.08" in result


async def test_read_store(db_session, seeded_data_for_tools):
    result = await read_store(db_session, "EUR_USD")
    assert isinstance(result, dict)
    assert "H1" in result
    assert result["H1"]["rsi_14"] == 55.3


async def test_read_insights(db_session, seeded_data_for_tools):
    result = await read_insights(db_session, "EUR_USD")
    assert isinstance(result, list)
    assert len(result) >= 1
    assert result[0]["agent_name"] == "session_agent"


def test_read_skill():
    result = read_skill("smc/fair_value_gap.md")
    assert isinstance(result, str)
    # This will return "Skill not found" until Task 5 creates the files
    # After Task 5: assert "Fair Value Gap" in result


def test_get_session_info():
    result = get_session_info()
    assert "current_session" in result
    assert "utc_hour" in result
