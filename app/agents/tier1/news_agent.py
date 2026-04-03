from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import run_agent
from app.agents.tools.news import fetch_news
from app.agents.tools.skills import read_skill

AGENT_NAME = "news_agent"
INSIGHT_TYPE = "news"
TTL_MINUTES = 15

SYSTEM_PROMPT = (
    "You are a financial news analyst agent for the NightShift "
    "trading platform.\n"
    "Fetch recent financial news, classify each headline by market "
    "impact (high/medium/low),\nand determine overall sentiment.\n"
    'Respond with JSON: {"headlines": [{"title": "...", '
    '"source": "...", "sentiment": 0.7, "impact": "high"}], '
    '"overall_sentiment": "bullish"|"bearish"|"neutral", '
    '"high_impact_events": ["..."]}'
)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "fetch_news",
            "description": "Fetch recent financial news",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "default": "general",
                    },
                },
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
        "fetch_news": lambda **kwargs: fetch_news(**kwargs),
        "read_skill": lambda **kwargs: read_skill(**kwargs),
    }
    result = await run_agent(
        name=AGENT_NAME,
        system_prompt=SYSTEM_PROMPT,
        user_message=(
            f"Analyze recent financial news relevant to {symbol}. "
            "Classify impact and sentiment."
        ),
        tools=TOOLS,
        tool_handlers=handlers,
    )
    result["_ttl_minutes"] = TTL_MINUTES
    return result
