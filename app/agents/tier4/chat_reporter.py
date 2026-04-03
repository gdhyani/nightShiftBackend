import json

from app.agents.base import run_agent

AGENT_NAME = "chat_reporter"

SYSTEM_PROMPT = """You are a daily report writer for the NightShift trading platform.
You receive performance stats and trade reviews, and must write a clear, concise daily report.

Respond with JSON:
{
  "summary": "Brief overall summary of the day's trading performance...",
  "highlights": ["highlight 1", "highlight 2"],
  "improvements": ["improvement suggestion 1", "improvement suggestion 2"]
}"""


async def run(performance: dict, review: dict) -> dict:
    user_message = (
        "Write a daily trading report based on this data:\n\n"
        f"Performance Stats:\n{json.dumps(performance, indent=2)}\n\n"
        f"Trade Reviews:\n{json.dumps(review, indent=2)}"
    )

    return await run_agent(
        name=AGENT_NAME,
        system_prompt=SYSTEM_PROMPT,
        user_message=user_message,
    )
