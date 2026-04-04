"""Paper trading engine with slippage simulation and charge calculation."""

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.trade import Position, Trade
from app.services.charge_calculator import ChargeCalculator


class PaperEngine:
    """Simulates order execution for paper trading."""

    def __init__(self, slippage_pct: float = 0.0005):
        self.slippage_pct = slippage_pct
        self.charge_calculator = ChargeCalculator()

    def _apply_slippage(self, price: float, side: str) -> float:
        """Apply slippage: BUY gets worse (higher), SELL gets worse (lower)."""
        if side.upper() == "BUY":
            return round(price * (1 + self.slippage_pct), 2)
        return round(price * (1 - self.slippage_pct), 2)

    async def place_order(
        self,
        session: AsyncSession,
        symbol: str,
        side: str,
        qty: float,
        order_type: str,
        price: float,
        strategy_id: int | None = None,
        product: str = "D",
    ) -> dict:
        """Place a paper order, creating Trade and Position records.

        Args:
            session: Async database session.
            symbol: Trading symbol.
            side: "BUY" or "SELL".
            qty: Order quantity.
            order_type: "MARKET" or "LIMIT".
            price: Order price.
            strategy_id: Optional strategy reference.
            product: "D" for delivery, "I" for intraday.

        Returns:
            Dict with order_id, status, symbol, side, qty, fill_price, charges, source.
        """
        fill_price = price
        if order_type.upper() == "MARKET":
            fill_price = self._apply_slippage(price, side)

        charges = self.charge_calculator.calculate(symbol, side, qty, fill_price, product=product)

        now = datetime.now(timezone.utc)
        trade = Trade(
            strategy_id=strategy_id,
            symbol=symbol,
            direction=side.upper(),
            entry_price=fill_price,
            stop_loss=0.0,
            take_profit=0.0,
            quantity=qty,
            status="open",
            source="paper",
            opened_at=now,
        )
        session.add(trade)
        await session.flush()

        position = Position(
            trade_id=trade.id,
            symbol=symbol,
            direction=side.upper(),
            entry_price=fill_price,
            current_price=fill_price,
            stop_loss=0.0,
            take_profit=0.0,
            quantity=qty,
            unrealized_pnl=0.0,
            status="open",
            opened_at=now,
        )
        session.add(position)
        await session.flush()

        return {
            "order_id": trade.id,
            "status": "filled",
            "symbol": symbol,
            "side": side.upper(),
            "qty": qty,
            "fill_price": fill_price,
            "charges": charges,
            "source": "paper",
        }

    async def close_trade(
        self,
        session: AsyncSession,
        trade_id: int,
        exit_price: float,
    ) -> dict:
        """Close an existing paper trade.

        Args:
            session: Async database session.
            trade_id: ID of the trade to close.
            exit_price: Price at which to close.

        Returns:
            Dict with order_id, status, pnl, exit_price.
        """
        trade = await session.get(Trade, trade_id)
        if trade is None:
            raise ValueError(f"Trade {trade_id} not found")

        # Apply slippage in the opposite direction of the original trade
        close_side = "SELL" if trade.direction == "BUY" else "BUY"
        slipped_exit = self._apply_slippage(exit_price, close_side)

        # Calculate P&L
        if trade.direction == "BUY":
            pnl = round((slipped_exit - trade.entry_price) * trade.quantity, 2)
        else:
            pnl = round((trade.entry_price - slipped_exit) * trade.quantity, 2)

        now = datetime.now(timezone.utc)
        trade.exit_price = slipped_exit
        trade.pnl = pnl
        trade.status = "closed"
        trade.closed_at = now

        # Update position
        from sqlalchemy import select

        stmt = select(Position).where(
            Position.trade_id == trade_id, Position.status == "open"
        )
        result = await session.execute(stmt)
        position = result.scalar_one_or_none()
        if position:
            position.status = "closed"
            position.current_price = slipped_exit
            position.unrealized_pnl = pnl

        await session.flush()

        return {
            "order_id": trade_id,
            "status": "closed",
            "pnl": pnl,
            "exit_price": slipped_exit,
        }
