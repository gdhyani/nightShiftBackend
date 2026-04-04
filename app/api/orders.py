import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_session
from app.services.charge_calculator import ChargeCalculator
from app.services.paper_engine import PaperEngine
from app.services.token_manager import TokenManager
from app.services.trading_context import TradingContext
from app.services.upstox import UpstoxService
from app.utils.encryption import generate_key

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/orders", tags=["orders"])
_enc_key = settings.token_encryption_key or generate_key()


def _build_context(session: AsyncSession) -> TradingContext:
    return TradingContext(
        session=session,
        token_manager=TokenManager(encryption_key=_enc_key),
        upstox=UpstoxService(base_url=settings.upstox_api_base_url),
        paper_engine=PaperEngine(),
        charge_calc=ChargeCalculator(),
        mode=settings.default_trading_mode,
    )


class PlaceOrderRequest(BaseModel):
    symbol: str
    side: str
    qty: int
    order_type: str = "MARKET"
    price: float = 0
    product: str = "D"


@router.post("")
async def place_order(data: PlaceOrderRequest, session: AsyncSession = Depends(get_session)):
    ctx = _build_context(session)
    return await ctx.place_order(symbol=data.symbol, side=data.side, qty=data.qty,
                                order_type=data.order_type, price=data.price)


class ModifyOrderRequest(BaseModel):
    qty: int | None = None
    price: float | None = None


@router.put("/{order_id}")
async def modify_order(
    order_id: str, data: ModifyOrderRequest,
    session: AsyncSession = Depends(get_session),
):
    ctx = _build_context(session)
    return await ctx.modify_order(order_id, data.qty, data.price)


@router.delete("/{order_id}")
async def cancel_order(order_id: str, session: AsyncSession = Depends(get_session)):
    ctx = _build_context(session)
    return await ctx.cancel_order(order_id)
