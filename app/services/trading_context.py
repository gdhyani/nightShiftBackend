import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Position
from app.services.charge_calculator import ChargeCalculator
from app.services.paper_engine import PaperEngine
from app.services.token_manager import TokenManager
from app.services.upstox import UpstoxService
from app.services.upstox_order_service import UpstoxOrderService

logger = logging.getLogger(__name__)


class TradingContext:
    def __init__(self, session, token_manager, upstox, paper_engine,
                 charge_calc, mode="paper", user_id="default"):
        self._session = session
        self._tm = token_manager
        self._upstox = upstox
        self._paper = paper_engine
        self._charges = charge_calc
        self._mode = mode
        self._user_id = user_id
        self._order_svc = UpstoxOrderService(upstox)

    def get_mode(self) -> str:
        return self._mode

    async def get_quote(self, symbol) -> dict:
        token = await self._tm.get_read_token(self._session, self._user_id)
        if not token:
            return {"error": "No valid token"}
        data = await self._upstox.get_ltp([symbol], token)
        return data.get(symbol, {})

    async def get_candles(self, symbol, unit, interval, days) -> list:
        token = await self._tm.get_read_token(self._session, self._user_id)
        if not token:
            return []
        from datetime import datetime, timedelta, timezone
        now = datetime.now(timezone.utc)
        from_date = (now - timedelta(days=days)).strftime("%Y-%m-%d")
        to_date = now.strftime("%Y-%m-%d")
        return await self._upstox.get_historical_candles(
            instrument_key=symbol, unit=unit, interval=interval,
            from_date=from_date, to_date=to_date, token=token,
        )

    async def get_positions(self) -> list[dict]:
        result = await self._session.execute(
            select(Position).where(Position.status == "open")
        )
        return [{"id": p.id, "symbol": p.symbol, "direction": p.direction,
                 "entry_price": p.entry_price, "quantity": p.quantity}
                for p in result.scalars().all()]

    async def place_order(self, symbol, side, qty, order_type="MARKET",
                         price=0, strategy_id=None) -> dict:
        if self._mode == "paper":
            fill_price = price
            if price == 0:
                quote = await self.get_quote(symbol)
                fill_price = quote.get("last_price", 0)
            return await self._paper.place_order(
                session=self._session, symbol=symbol, side=side, qty=qty,
                order_type=order_type, price=fill_price, strategy_id=strategy_id,
            )
        token, mode_used = await self._tm.get_write_token(
            self._session, self._user_id, self._mode
        )
        if not token:
            return {"error": "No valid token", "status": mode_used}
        return await self._order_svc.place_order(
            token=token, symbol=symbol, side=side, qty=qty,
            order_type=order_type, price=price,
        )

    async def modify_order(self, order_id, qty=None, price=None) -> dict:
        if self._mode == "paper":
            return {"status": "not_supported_in_paper"}
        token, _ = await self._tm.get_write_token(self._session, self._user_id, self._mode)
        if not token:
            return {"error": "No valid token"}
        return await self._order_svc.modify_order(token, order_id, qty, price)

    async def cancel_order(self, order_id) -> dict:
        if self._mode == "paper":
            return {"status": "not_supported_in_paper"}
        token, _ = await self._tm.get_write_token(self._session, self._user_id, self._mode)
        if not token:
            return {"error": "No valid token"}
        return await self._order_svc.cancel_order(token, order_id)

    async def calculate_charges(self, symbol, side, qty, price) -> dict:
        return self._charges.calculate(symbol=symbol, side=side, qty=qty, price=price)
