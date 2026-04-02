import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Trade, Position

logger = logging.getLogger(__name__)


class MockExecutor:
    async def open_trade(
        self,
        session: AsyncSession,
        strategy_id: int,
        symbol: str,
        direction: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        quantity: float,
        reasoning: dict | None = None,
    ) -> Trade:
        now = datetime.now(timezone.utc)
        trade = Trade(
            strategy_id=strategy_id,
            symbol=symbol,
            direction=direction,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            quantity=quantity,
            status="open",
            reasoning=reasoning,
            opened_at=now,
        )
        session.add(trade)
        await session.flush()

        position = Position(
            trade_id=trade.id,
            symbol=symbol,
            direction=direction,
            entry_price=entry_price,
            current_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            quantity=quantity,
            unrealized_pnl=0.0,
            status="open",
        )
        session.add(position)
        await session.flush()

        logger.info(f"[MOCK] Opened {direction} {symbol} @ {entry_price} (trade #{trade.id})")
        return trade

    async def close_trade(
        self,
        session: AsyncSession,
        trade_id: int,
        exit_price: float,
    ) -> Trade:
        result = await session.execute(select(Trade).where(Trade.id == trade_id))
        trade = result.scalar_one()

        if trade.direction == "BUY":
            pnl = (exit_price - trade.entry_price) * trade.quantity
        else:
            pnl = (trade.entry_price - exit_price) * trade.quantity

        trade.exit_price = exit_price
        trade.pnl = pnl
        trade.status = "closed"
        trade.closed_at = datetime.now(timezone.utc)

        pos_result = await session.execute(
            select(Position).where(Position.trade_id == trade_id)
        )
        position = pos_result.scalar_one_or_none()
        if position:
            position.status = "closed"
            position.current_price = exit_price
            position.unrealized_pnl = pnl

        await session.flush()
        logger.info(f"[MOCK] Closed trade #{trade_id} @ {exit_price} P&L: {pnl:.5f}")
        return trade
