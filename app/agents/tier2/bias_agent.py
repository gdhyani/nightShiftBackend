from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import run_agent
from app.agents.tools.market_data import read_candles, read_store
from app.agents.tools.insights import read_insights
from app.agents.tools.skills import read_skill

AGENT_NAME = "bias_agent"
INSIGHT_TYPE = "bias"
TTL_MINUTES = 480

SYSTEM_PROMPT = """You are a directional bias agent for the NightShift trading platform.
Determine directional bias from HTF structure and trend alignment.
Respond with JSON: {"direction": "bullish"|"bearish"|"neutral", "confidence": 0.72, "reasoning": "...", "htf_trend": "bullish", "ltf_trend": "neutral"}"""

TOOLS = [
    {"type": "function", "function": {"name": "read_candles", "description": "Read candles", "parameters": {"type": "object", "properties": {"symbol": {"type": "string"}, "timeframe": {"type": "string"}, "count": {"type": "integer", "default": 50}}, "required": ["symbol", "timeframe"]}}},
    {"type": "function", "function": {"name": "read_store", "description": "Read store snapshot", "parameters": {"type": "object", "properties": {"symbol": {"type": "string"}}, "required": ["symbol"]}}},
    {"type": "function", "function": {"name": "read_insights", "description": "Read recent agent insights", "parameters": {"type": "object", "properties": {"symbol": {"type": "string"}, "agent_name": {"type": "string"}}, "required": ["symbol"]}}},
    {"type": "function", "function": {"name": "read_skill", "description": "Read a SKILL.md file", "parameters": {"type": "object", "properties": {"skill_path": {"type": "string"}}, "required": ["skill_path"]}}},
]


async def run(session: AsyncSession, symbol: str) -> dict:
    handlers = {
        "read_candles": lambda **kwargs: read_candles(session, **kwargs),
        "read_store": lambda **kwargs: read_store(session, **kwargs),
        "read_insights": lambda **kwargs: read_insights(session, **kwargs),
        "read_skill": lambda **kwargs: read_skill(**kwargs),
    }
    result = await run_agent(
        name=AGENT_NAME,
        system_prompt=SYSTEM_PROMPT,
        user_message=f"Determine directional bias for {symbol}.",
        tools=TOOLS,
        tool_handlers=handlers,
    )
    result["_ttl_minutes"] = TTL_MINUTES
    return result
