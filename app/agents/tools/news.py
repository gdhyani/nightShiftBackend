import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


async def fetch_news(symbol: str | None = None, category: str = "general") -> list[dict]:
    if not settings.finnhub_api_key:
        return [{"error": "Finnhub API key not configured"}]
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.get(
                "https://finnhub.io/api/v1/news",
                params={"category": category, "token": settings.finnhub_api_key},
            )
            response.raise_for_status()
            articles = response.json()
            return [
                {"headline": a.get("headline", ""), "summary": a.get("summary", "")[:200],
                 "source": a.get("source", ""), "datetime": a.get("datetime", 0),
                 "related": a.get("related", "")}
                for a in articles[:10]
            ]
        except Exception as e:
            logger.error(f"Finnhub news fetch failed: {e}")
            return [{"error": str(e)}]
