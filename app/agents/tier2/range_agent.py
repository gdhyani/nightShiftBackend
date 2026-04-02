from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import run_agent
from app.agents.tools.market_data import read_candles, read_store
from app.agents.tools.skills import read_skill

AGENT_NAME = "range_agent"
INSIGHT_TYPE = "ranges"
TTL_MINUTES = 120

SYSTEM_PROMPT = """You are a range analysis agent for the NightShift trading platform.
Define current dealing range, premium/discount zones, key levels.
Respond with JSON: {"range_high": 1.0920, "range_low": 1.0830, "premium_zone": [1.0890, 1.0920], "discount_zone": [1.0830, 1.0860], "equilibrium": 1.0875, "key_levels": [1.0850, 1.0900]}"""

TOOLS = [
    {"type": "function", "function": {"name": "read_candles", "description": "Read candles", "parameters": {"type": "object", "properties": {"symbol": {"type": "string"}, "timeframe": {"type": "string"}, "count": {"type": "integer", "default": 100}}, "required": ["symbol", "timeframe"]}}},
    {"type": "function", "function": {"name": "read_store", "description": "Read store snapshot", "parameters": {"type": "object", "properties": {"symbol": {"type": "string"}}, "required": ["symbol"]}}},
    {"type": "function", "function": {"name": "read_skill", "description": "Read a SKILL.md file", "parameters": {"type": "object", "properties": {"skill_path": {"type": "string"}}, "required": ["skill_path"]}}},
]


async def run(session: AsyncSession, symbol: str) -> dict:
    handlers = {
        "read_candles": lambda **kwargs: read_candles(session, **kwargs),
        "read_store": lambda **kwargs: read_store(session, **kwargs),
        "read_skill": lambda **kwargs: read_skill(**kwargs),
    }
    result = await run_agent(
        name=AGENT_NAME,
        system_prompt=SYSTEM_PROMPT,
        user_message=f"Define the current dealing range for {symbol}.",
        tools=TOOLS,
        tool_handlers=handlers,
    )
    result["_ttl_minutes"] = TTL_MINUTES
    return result
