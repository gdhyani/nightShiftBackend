from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import run_agent
from app.agents.tools.market_data import read_candles, read_store
from app.agents.tools.skills import read_skill

AGENT_NAME = "structure_agent"
INSIGHT_TYPE = "structure"
TTL_MINUTES = 120

SYSTEM_PROMPT = (
    "You are a market structure agent for the NightShift "
    "trading platform.\n"
    "Track market structure across timeframes -- BOS, CHoCH, "
    "swing points, trend shifts.\n"
    'Respond with JSON: {"h1_structure": '
    '"bullish"|"bearish"|"ranging", '
    '"h4_structure": "bullish"|"bearish"|"ranging", '
    '"last_bos": {"price": 1.0880, "timeframe": "H1", '
    '"direction": "bullish"}|null, "last_choch": null, '
    '"swing_high": 1.0920, "swing_low": 1.0830}'
)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_candles",
            "description": "Read candles",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                    "timeframe": {"type": "string"},
                    "count": {"type": "integer", "default": 100},
                },
                "required": ["symbol", "timeframe"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_store",
            "description": "Read store snapshot",
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
        user_message=f"Analyze market structure for {symbol}.",
        tools=TOOLS,
        tool_handlers=handlers,
    )
    result["_ttl_minutes"] = TTL_MINUTES
    return result
