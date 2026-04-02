from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models import Trade, TradeSchema, Position, PositionSchema

router = APIRouter(tags=["trades"])


@router.get("/api/trades", response_model=list[TradeSchema])
async def list_trades(
    strategy_id: int | None = Query(None),
    symbol: str | None = Query(None),
    status: str | None = Query(None),
    limit: int = 50,
    session: AsyncSession = Depends(get_session),
):
    query = select(Trade).order_by(Trade.created_at.desc()).limit(limit)
    if strategy_id:
        query = query.where(Trade.strategy_id == strategy_id)
    if symbol:
        query = query.where(Trade.symbol == symbol)
    if status:
        query = query.where(Trade.status == status)
    result = await session.execute(query)
    return result.scalars().all()


@router.get("/api/trades/{trade_id}", response_model=TradeSchema)
async def get_trade(trade_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Trade).where(Trade.id == trade_id))
    trade = result.scalar_one_or_none()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    return trade


@router.get("/api/positions", response_model=list[PositionSchema])
async def list_positions(session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(Position).where(Position.status == "open").order_by(Position.opened_at.desc())
    )
    return result.scalars().all()
