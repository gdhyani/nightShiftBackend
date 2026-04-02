from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import run_agent
from app.agents.tools.market_data import read_candles, read_store
from app.agents.tools.skills import read_skill

AGENT_NAME = "correlation_agent"
INSIGHT_TYPE = "correlations"
TTL_MINUTES = 60

SYSTEM_PROMPT = """You are a correlation analysis agent for the NightShift trading platform.
Analyze correlations between symbols, check USD strength, detect divergences.
Respond with JSON: {"correlations": {"EUR_USD_GBP_USD": 0.85}, "usd_strength": "strengthening"|"weakening"|"neutral", "divergences": ["..."]}"""

TOOLS = [
    {"type": "function", "function": {"name": "read_candles", "description": "Read recent candles", "parameters": {"type": "object", "properties": {"symbol": {"type": "string"}, "timeframe": {"type": "string"}, "count": {"type": "integer", "default": 50}}, "required": ["symbol", "timeframe"]}}},
    {"type": "function", "function": {"name": "read_store", "description": "Read indicator snapshot", "parameters": {"type": "object", "properties": {"symbol": {"type": "string"}}, "required": ["symbol"]}}},
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
        user_message=f"Analyze correlations for {symbol} against other watched pairs.",
        tools=TOOLS,
        tool_handlers=handlers,
    )
    result["_ttl_minutes"] = TTL_MINUTES
    return result
