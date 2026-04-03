import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_session
from app.services.token_manager import TokenManager
from app.services.upstox import UpstoxService
from app.utils.encryption import generate_key

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/market", tags=["market"])

_enc_key = settings.token_encryption_key or generate_key()


def _get_upstox() -> UpstoxService:
    return UpstoxService(base_url=settings.upstox_api_base_url)


def _get_tm() -> TokenManager:
    return TokenManager(encryption_key=_enc_key)


@router.get("/quote/{instrument_key:path}")
async def get_market_quote(
    instrument_key: str,
    session: AsyncSession = Depends(get_session),
):
    tm = _get_tm()
    token = await tm.get_read_token(session)
    if not token:
        return {"error": "No valid Upstox token", "status": "awaiting_auth"}
    upstox = _get_upstox()
    try:
        data = await upstox.get_ltp([instrument_key], token)
        return data.get(instrument_key, {"error": "No data"})
    except Exception as e:
        logger.error(f"Quote fetch failed: {e}")
        return {"error": str(e)}


@router.get("/quotes")
async def get_market_quotes(
    keys: str = Query(..., description="Comma-separated instrument keys"),
    session: AsyncSession = Depends(get_session),
):
    tm = _get_tm()
    token = await tm.get_read_token(session)
    if not token:
        return {"error": "No valid Upstox token", "status": "awaiting_auth"}
    upstox = _get_upstox()
    key_list = [k.strip() for k in keys.split(",")]
    try:
        return await upstox.get_ltp(key_list, token)
    except Exception as e:
        logger.error(f"Quotes fetch failed: {e}")
        return {"error": str(e)}


@router.get("/candles/{instrument_key:path}")
async def get_historical_candles(
    instrument_key: str,
    unit: str = Query("minutes"),
    interval: int = Query(5),
    from_date: str = Query(...),
    to_date: str = Query(...),
    session: AsyncSession = Depends(get_session),
):
    tm = _get_tm()
    token = await tm.get_read_token(session)
    if not token:
        return {"error": "No valid Upstox token", "status": "awaiting_auth"}
    upstox = _get_upstox()
    try:
        return await upstox.get_historical_candles(
            instrument_key=instrument_key, unit=unit, interval=interval,
            from_date=from_date, to_date=to_date, token=token,
        )
    except Exception as e:
        logger.error(f"Historical candles failed: {e}")
        return {"error": str(e)}


@router.get("/candles/intraday/{instrument_key:path}")
async def get_intraday_candles(
    instrument_key: str,
    unit: str = Query("minutes"),
    interval: int = Query(1),
    session: AsyncSession = Depends(get_session),
):
    tm = _get_tm()
    token = await tm.get_read_token(session)
    if not token:
        return {"error": "No valid Upstox token", "status": "awaiting_auth"}
    upstox = _get_upstox()
    try:
        return await upstox.get_intraday_candles(
            instrument_key=instrument_key, unit=unit, interval=interval, token=token,
        )
    except Exception as e:
        logger.error(f"Intraday candles failed: {e}")
        return {"error": str(e)}
