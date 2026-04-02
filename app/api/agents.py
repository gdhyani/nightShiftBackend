from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models import AgentInsight, AgentInsightSchema
from app.services.agent_runner import AgentRunner

router = APIRouter(prefix="/api/agents", tags=["agents"])


@router.get("")
async def list_agents():
    return AgentRunner.list_agents()


@router.get("/insights", response_model=list[AgentInsightSchema])
async def get_agent_insights(
    symbol: str | None = Query(None),
    agent_name: str | None = Query(None),
    limit: int = 50,
    session: AsyncSession = Depends(get_session),
):
    query = select(AgentInsight).order_by(AgentInsight.created_at.desc()).limit(limit)
    if symbol:
        query = query.where(AgentInsight.symbol == symbol)
    if agent_name:
        query = query.where(AgentInsight.agent_name == agent_name)
    result = await session.execute(query)
    return result.scalars().all()
