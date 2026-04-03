from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AgentInsight


async def read_insights(
    session: AsyncSession,
    symbol: str,
    agent_name: str | None = None,
) -> list[dict]:
    now = datetime.now(timezone.utc)
    query = (
        select(AgentInsight)
        .where(AgentInsight.symbol == symbol, AgentInsight.expires_at > now)
        .order_by(AgentInsight.created_at.desc()).limit(20)
    )
    if agent_name:
        query = query.where(AgentInsight.agent_name == agent_name)
    result = await session.execute(query)
    return [
        {"agent_name": i.agent_name, "insight_type": i.insight_type, "data": i.data,
         "confidence": i.confidence, "created_at": i.created_at.isoformat()}
        for i in result.scalars().all()
    ]
