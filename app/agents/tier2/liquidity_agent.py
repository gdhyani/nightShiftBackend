from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import run_agent
from app.agents.tools.insights import read_insights
from app.agents.tools.market_data import read_candles
from app.agents.tools.skills import read_skill

AGENT_NAME = "liquidity_agent"
INSIGHT_TYPE = "liquidity"
TTL_MINUTES = 120

SYSTEM_PROMPT = (
    "You are a liquidity mapping agent for the NightShift "
    "trading platform.\n"
    "Map where liquidity pools sit -- equal highs/lows, "
    "trendline liquidity, session targets.\n"
    'Respond with JSON: {"buy_side_liquidity": [1.0920], '
    '"sell_side_liquidity": [1.0810], "equal_highs": [1.0920], '
    '"equal_lows": [], "likely_target": "buy_side_1.0920"}'
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
            "name": "read_insights",
            "description": "Read agent insights",
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
        "read_insights": lambda **kwargs: read_insights(session, **kwargs),
        "read_skill": lambda **kwargs: read_skill(**kwargs),
    }
    result = await run_agent(
        name=AGENT_NAME,
        system_prompt=SYSTEM_PROMPT,
        user_message=f"Map liquidity for {symbol}.",
        tools=TOOLS,
        tool_handlers=handlers,
    )
    result["_ttl_minutes"] = TTL_MINUTES
    return result
