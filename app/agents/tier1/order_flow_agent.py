from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import run_agent
from app.agents.tools.market_data import read_candles, read_store
from app.agents.tools.skills import read_skill

AGENT_NAME = "order_flow_agent"
INSIGHT_TYPE = "order_flow"
TTL_MINUTES = 5

SYSTEM_PROMPT = (
    "You are an order flow analysis agent for the NightShift "
    "trading platform.\n"
    "Analyze recent candles for volume imbalances, engulfing "
    "patterns, pin bars, absorption signals.\n"
    'Respond with JSON: {"volume_imbalance": '
    '"bullish"|"bearish"|"neutral", '
    '"patterns": ["pattern_at_price"], '
    '"absorption_detected": false, '
    '"dominant_side": "buyers"|"sellers"|"neutral"}'
)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_candles",
            "description": "Read recent candles",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "timeframe": {"type": "string"},
                    "count": {"type": "integer", "default": 60},
                },
                "required": ["symbol", "timeframe"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_store",
            "description": "Read indicator snapshot",
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
            "name": "read_skill",
            "description": "Read a SKILL.md file",
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
        "read_skill": lambda **kwargs: read_skill(**kwargs),
    }
    result = await run_agent(
        name=AGENT_NAME,
        system_prompt=SYSTEM_PROMPT,
        user_message=f"Analyze order flow for {symbol} using recent M1 candles.",
        tools=TOOLS,
        tool_handlers=handlers,
    )
    result["_ttl_minutes"] = TTL_MINUTES
    return result
