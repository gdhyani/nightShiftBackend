import logging
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_session
from app.services.token_manager import TokenManager
from app.services.upstox import UpstoxService
from app.utils.encryption import generate_key

logger = logging.getLogger(__name__)

router = APIRouter()

# Use configured key or generate one for development
_encryption_key = settings.token_encryption_key or generate_key()


def _get_token_manager() -> TokenManager:
    return TokenManager(encryption_key=_encryption_key)


# ── Pydantic request/response models ──


class ModeRequest(BaseModel):
    mode: str


class SandboxTokenRequest(BaseModel):
    token: str
    expires_in_days: int = 30


class WebhookTokenPayload(BaseModel):
    client_id: str = ""
    user_id: str = "default"
    access_token: str
    token_type: str = "Bearer"
    expires_at: str = ""
    message_type: str = "access_token"


# ── Auth endpoints ──


@router.get("/api/auth/upstox/login")
async def upstox_login():
    params = urlencode({
        "response_type": "code",
        "client_id": settings.upstox_client_id,
        "redirect_uri": settings.upstox_redirect_uri,
    })
    login_url = f"https://api.upstox.com/v2/login/authorization/dialog?{params}"
    return {"login_url": login_url}


@router.get("/api/auth/upstox/callback")
async def upstox_callback(
    code: str,
    session: AsyncSession = Depends(get_session),
):
    tm = _get_token_manager()
    svc = UpstoxService(base_url=settings.upstox_api_base_url)
    try:
        result = await svc.exchange_auth_code(
            code=code,
            client_id=settings.upstox_client_id,
            client_secret=settings.upstox_client_secret,
            redirect_uri=settings.upstox_redirect_uri,
        )
        token = result.get("access_token")
        if not token:
            return {"status": "error", "detail": "No access_token in response"}

        expires_in = result.get("expires_in", 86400)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        await tm.store_daily_token(session, "default", token, expires_at)
        return {"status": "ok", "mode": "daily_token_stored"}
    finally:
        await svc.close()


@router.post("/api/auth/upstox/token-request")
async def upstox_token_request():
    svc = UpstoxService(base_url=settings.upstox_api_base_url)
    try:
        result = await svc.request_daily_token(
            client_id=settings.upstox_client_id,
            client_secret=settings.upstox_client_secret,
        )
        return result
    finally:
        await svc.close()


@router.get("/api/auth/upstox/status")
async def upstox_auth_status(
    session: AsyncSession = Depends(get_session),
):
    tm = _get_token_manager()
    status = await tm.get_token_status(session, "default")
    return status


@router.post("/api/webhooks/upstox/token")
async def upstox_token_webhook(
    payload: WebhookTokenPayload,
    session: AsyncSession = Depends(get_session),
):
    tm = _get_token_manager()
    user_id = payload.user_id or "default"

    # Parse expires_at (Upstox sends milliseconds timestamp)
    if payload.expires_at:
        try:
            ts = int(payload.expires_at) / 1000
            expires_at = datetime.fromtimestamp(ts, tz=timezone.utc)
        except (ValueError, OSError):
            expires_at = datetime.now(timezone.utc) + timedelta(hours=8)
    else:
        expires_at = datetime.now(timezone.utc) + timedelta(hours=8)

    await tm.store_daily_token(session, user_id, payload.access_token, expires_at)
    logger.info(f"Stored daily token for user {user_id} via webhook")
    return {"status": "ok"}


# ── Trading config endpoints ──


@router.get("/api/trading/config")
async def get_trading_config(
    session: AsyncSession = Depends(get_session),
):
    tm = _get_token_manager()
    status = await tm.get_token_status(session, "default")
    return status


@router.put("/api/trading/mode")
async def switch_trading_mode(
    body: ModeRequest,
    session: AsyncSession = Depends(get_session),
):
    tm = _get_token_manager()
    config = await tm.get_or_create_config(session, "default")
    config.default_mode = body.mode
    config.updated_at = datetime.now(timezone.utc)
    await session.commit()
    return {"mode": config.default_mode}


@router.post("/api/trading/tokens/sandbox")
async def update_sandbox_token(
    body: SandboxTokenRequest,
    session: AsyncSession = Depends(get_session),
):
    tm = _get_token_manager()
    expires_at = datetime.now(timezone.utc) + timedelta(days=body.expires_in_days)
    await tm.store_sandbox_token(session, "default", body.token, expires_at)
    return {"status": "ok", "expires_at": expires_at.isoformat()}


@router.post("/api/webhooks/upstox/orders")
async def webhook_order_update(
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    body = await request.json()
    order_id = body.get("order_id")
    status = body.get("status")
    if order_id and status:
        from app.models import Trade
        result = await session.execute(
            select(Trade).where(Trade.id == int(order_id))
        )
        trade = result.scalar_one_or_none()
        if trade:
            if status in ("complete", "filled"):
                trade.status = "open"
                avg_price = body.get("average_price")
                if avg_price:
                    trade.entry_price = float(avg_price)
            elif status in ("rejected", "cancelled"):
                trade.status = "cancelled"
            await session.commit()
        logger.info(f"Order webhook: {order_id} -> {status}")
    return {"status": "ok"}
