import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import run_agent
from app.agents.tools.skills import read_skill
from app.models import Position

AGENT_NAME = "evaluator_agent"
INSIGHT_TYPE = "evaluation"
TTL_MINUTES = 15

SYSTEM_PROMPT = """You are an evaluator agent for the NightShift trading platform.
You receive the analyst agent's output and decide whether to execute a trade.

Consider:
- Confluence score and signal alignment
- Current open positions (avoid overexposure)
- Risk/reward ratio (minimum 1:2)
- Key levels and entry zone quality

Respond with JSON:
{
  "decision": "EXECUTE"|"WAIT"|"SKIP",
  "entry_price": 1.0850,
  "stop_loss": 1.0820,
  "take_profit": 1.0920,
  "quantity": 0.1,
  "direction": "BUY"|"SELL",
  "confidence": 0.0-1.0,
  "reasoning": "Why this decision was made..."
}

If decision is WAIT or SKIP, entry_price/stop_loss/take_profit/quantity can be null."""

TOOLS = [
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
    {
        "type": "function",
        "function": {
            "name": "get_open_positions",
            "description": "Get currently open positions",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string"},
                },
                "required": [],
            },
        },
    },
]


async def _get_open_positions(session: AsyncSession, symbol: str | None = None) -> list[dict]:
    query = select(Position).where(Position.status == "open")
    if symbol:
        query = query.where(Position.symbol == symbol)
    result = await session.execute(query)
    positions = result.scalars().all()
    return [
        {
            "id": p.id,
            "trade_id": p.trade_id,
            "symbol": p.symbol,
            "direction": p.direction,
            "entry_price": p.entry_price,
            "current_price": p.current_price,
            "quantity": p.quantity,
            "unrealized_pnl": p.unrealized_pnl,
        }
        for p in positions
    ]


async def run(session: AsyncSession, symbol: str, analysis: dict) -> dict:
    handlers = {
        "read_skill": lambda **kwargs: read_skill(**kwargs),
        "get_open_positions": lambda **kwargs: _get_open_positions(session, **kwargs),
    }
    result = await run_agent(
        name=AGENT_NAME,
        system_prompt=SYSTEM_PROMPT,
        user_message=(
            f"Evaluate the following analysis for {symbol} "
            "and decide whether to execute a trade.\n\n"
            f"Analysis:\n{json.dumps(analysis, indent=2)}"
        ),
        tools=TOOLS,
        tool_handlers=handlers,
    )
    result["_ttl_minutes"] = TTL_MINUTES
    return result
