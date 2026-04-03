from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models import (
    Strategy,
    StrategyCreate,
    StrategyRun,
    StrategyRunSchema,
    StrategySchema,
    StrategyUpdate,
)

router = APIRouter(prefix="/api/strategies", tags=["strategies"])


@router.get("", response_model=list[StrategySchema])
async def list_strategies(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Strategy).order_by(Strategy.created_at.desc()))
    return result.scalars().all()


@router.post("", response_model=StrategySchema)
async def create_strategy(data: StrategyCreate, session: AsyncSession = Depends(get_session)):
    strategy = Strategy(
        name=data.name, symbols=data.symbols, enabled=data.enabled,
        schedule_interval=data.schedule_interval, event_triggers=data.event_triggers,
        pipeline_config=data.pipeline_config,
    )
    session.add(strategy)
    await session.commit()
    await session.refresh(strategy)
    return strategy


@router.get("/{strategy_id}", response_model=StrategySchema)
async def get_strategy(strategy_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Strategy).where(Strategy.id == strategy_id))
    strategy = result.scalar_one_or_none()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy


@router.patch("/{strategy_id}", response_model=StrategySchema)
async def update_strategy(
    strategy_id: int,
    data: StrategyUpdate,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Strategy).where(Strategy.id == strategy_id))
    strategy = result.scalar_one_or_none()
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(strategy, field, value)
    strategy.updated_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(strategy)
    return strategy


@router.get("/{strategy_id}/runs", response_model=list[StrategyRunSchema])
async def get_strategy_runs(
    strategy_id: int,
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(StrategyRun).where(StrategyRun.strategy_id == strategy_id)
        .order_by(StrategyRun.created_at.desc()).limit(limit)
    )
    return result.scalars().all()
