from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import run_agent
from app.agents.tools.insights import read_insights
from app.agents.tools.market_data import read_candles, read_store
from app.agents.tools.skills import read_skill

AGENT_NAME = "analyst_agent"
INSIGHT_TYPE = "analysis"
TTL_MINUTES = 30

SYSTEM_PROMPT = """You are an analyst agent for the NightShift trading platform.
Analyze market data, agent insights, indicators, and apply Smart Money Concepts (SMC) skills.
Synthesize all available information into a comprehensive trade analysis.

Respond with JSON:
{
  "direction": "bullish"|"bearish"|"neutral",
  "confluence_score": 0.0-1.0,
  "signals": ["signal1", "signal2"],
  "key_levels": {"resistance": [1.0900], "support": [1.0800]},
  "entry_zone": {"low": 1.0840, "high": 1.0860},
  "reasoning": "Detailed analysis reasoning..."
}"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_candles",
            "description": "Read recent candles for a symbol and timeframe",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "timeframe": {"type": "string"},
                    "count": {"type": "integer", "default": 50},
                },
                "required": ["symbol", "timeframe"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_store",
            "description": "Read store snapshot with indicators",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                },
                "required": ["symbol"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_insights",
            "description": "Read recent agent insights",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "agent_name": {"type": "string"},
                },
                "required": ["symbol"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_skill",
            "description": "Read a SKILL.md file for SMC concepts",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill_path": {"type": "string"},
                },
                "required": ["skill_path"],
            },
        },
    },
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
        user_message=(
            f"Perform a comprehensive market analysis for {symbol}. "
            "Read candles on multiple timeframes (H4, H1, M15), "
            "check the store snapshot, and review all available "
            "agent insights. Apply SMC skills if available."
        ),
        tools=TOOLS,
        tool_handlers=handlers,
    )
    result["_ttl_minutes"] = TTL_MINUTES
    return result
