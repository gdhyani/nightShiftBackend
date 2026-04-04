import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Account, Position, Trade
from app.services.upstox import UpstoxService

logger = logging.getLogger(__name__)


class PortfolioService:
    def __init__(self, upstox: UpstoxService | None = None):
        self._upstox = upstox

    async def get_holdings(self, session, token=None, mode="paper") -> list[dict]:
        if mode != "paper" and token and self._upstox:
            try:
                resp = await self._upstox._client.get(
                    "/v2/portfolio/long-term-holdings",
                    headers=self._upstox._auth_headers(token),
                )
                resp.raise_for_status()
                return resp.json().get("data", [])
            except Exception as e:
                logger.error(f"Holdings fetch failed: {e}")
                return []
        result = await session.execute(
            select(Trade).where(Trade.status == "open", Trade.source == "paper")
        )
        return [{"symbol": t.symbol, "quantity": t.quantity, "average_price": t.entry_price, "pnl": t.pnl or 0}
                for t in result.scalars().all()]

    async def get_positions(self, session, token=None, mode="paper") -> list[dict]:
        if mode != "paper" and token and self._upstox:
            try:
                resp = await self._upstox._client.get(
                    "/v2/portfolio/short-term-positions",
                    headers=self._upstox._auth_headers(token),
                )
                resp.raise_for_status()
                return resp.json().get("data", [])
            except Exception as e:
                logger.error(f"Positions fetch failed: {e}")
                return []
        result = await session.execute(select(Position).where(Position.status == "open"))
        return [{"symbol": p.symbol, "direction": p.direction, "entry_price": p.entry_price,
                 "current_price": p.current_price, "quantity": p.quantity, "unrealized_pnl": p.unrealized_pnl}
                for p in result.scalars().all()]

    async def get_margins(self, session, token=None, mode="paper") -> dict:
        if mode != "paper" and token and self._upstox:
            try:
                resp = await self._upstox._client.get(
                    "/v2/user/get-fund-and-margin",
                    headers=self._upstox._auth_headers(token),
                )
                resp.raise_for_status()
                return resp.json().get("data", {})
            except Exception as e:
                logger.error(f"Margins fetch failed: {e}")
        result = await session.execute(select(Account))
        account = result.scalar_one_or_none()
        if account:
            return {"balance": account.balance, "equity": account.equity,
                    "margin_used": account.margin_used, "available": account.balance - account.margin_used}
        return {"balance": 1000000.0, "equity": 1000000.0, "margin_used": 0.0, "available": 1000000.0}
