import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import run_agent
from app.models import Trade

AGENT_NAME = "trade_reviewer"

SYSTEM_PROMPT = """You are a trade review agent for the NightShift trading platform.
You receive a list of closed trades and must evaluate each one.

For each trade, assess:
- Entry quality (1-10): Was the entry at a good price level?
- Exit quality (1-10): Was the exit optimal or premature/late?
- Correct signals: What signals supported this trade?
- Wrong signals: What signals were missed or misread?
- Lesson: What can be learned from this trade?

Respond with JSON:
{
  "reviews": [
    {
      "trade_id": 1,
      "grade": "A"|"B"|"C"|"D"|"F",
      "entry_quality": 8,
      "exit_quality": 7,
      "correct_signals": ["signal1"],
      "wrong_signals": ["signal2"],
      "lesson": "..."
    }
  ],
  "overall_assessment": "Summary of all trades reviewed..."
}"""


async def run(session: AsyncSession) -> dict:
    result = await session.execute(
        select(Trade)
        .where(Trade.status == "closed")
        .order_by(Trade.closed_at.desc())
        .limit(20)
    )
    trades = result.scalars().all()

    if not trades:
        return {
            "reviews": [],
            "overall_assessment": "No closed trades to review.",
        }

    trades_data = []
    for t in trades:
        trades_data.append({
            "trade_id": t.id,
            "symbol": t.symbol,
            "direction": t.direction,
            "entry_price": t.entry_price,
            "exit_price": t.exit_price,
            "stop_loss": t.stop_loss,
            "take_profit": t.take_profit,
            "pnl": t.pnl,
            "reasoning": t.reasoning,
            "opened_at": t.opened_at.isoformat() if t.opened_at else None,
            "closed_at": t.closed_at.isoformat() if t.closed_at else None,
        })

    user_message = (
        f"Review these {len(trades_data)} closed trades:\n"
        f"{json.dumps(trades_data, indent=2)}"
    )

    return await run_agent(
        name=AGENT_NAME,
        system_prompt=SYSTEM_PROMPT,
        user_message=user_message,
    )
