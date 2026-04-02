from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import run_agent
from app.agents.tools.market_data import read_candles
from app.agents.tools.session import get_session_info
from app.agents.tools.skills import read_skill

AGENT_NAME = "session_agent"
INSIGHT_TYPE = "sessions"
TTL_MINUTES = 30

SYSTEM_PROMPT = """You are a trading session analyst agent for the NightShift trading platform.
Track current session, identify killzones, calculate session highs/lows.
Respond with JSON: {"current_session": "london"|"new_york"|"asia"|"off_hours", "killzone_active": true|false, "session_high": 1.0890, "session_low": 1.0835, "next_session": "new_york", "time_to_next": "3h 15m"}"""

TOOLS = [
    {"type": "function", "function": {"name": "get_session_info", "description": "Get current trading session info", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "read_candles", "description": "Read recent candles", "parameters": {"type": "object", "properties": {"symbol": {"type": "string"}, "timeframe": {"type": "string"}, "count": {"type": "integer", "default": 20}}, "required": ["symbol", "timeframe"]}}},
    {"type": "function", "function": {"name": "read_skill", "description": "Read a SKILL.md file", "parameters": {"type": "object", "properties": {"skill_path": {"type": "string"}}, "required": ["skill_path"]}}},
]


async def run(session: AsyncSession, symbol: str) -> dict:
    handlers = {
        "get_session_info": lambda **kwargs: get_session_info(),
        "read_candles": lambda **kwargs: read_candles(session, **kwargs),
        "read_skill": lambda **kwargs: read_skill(**kwargs),
    }
    result = await run_agent(
        name=AGENT_NAME,
        system_prompt=SYSTEM_PROMPT,
        user_message=f"Analyze current trading session for {symbol}.",
        tools=TOOLS,
        tool_handlers=handlers,
    )
    result["_ttl_minutes"] = TTL_MINUTES
    return result
