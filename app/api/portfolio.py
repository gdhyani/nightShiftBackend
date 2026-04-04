from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_session
from app.services.portfolio_service import PortfolioService
from app.services.token_manager import TokenManager
from app.services.upstox import UpstoxService
from app.utils.encryption import generate_key

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])
_enc_key = settings.token_encryption_key or generate_key()


@router.get("/holdings")
async def get_holdings(session: AsyncSession = Depends(get_session)):
    tm = TokenManager(encryption_key=_enc_key)
    token = await tm.get_read_token(session)
    svc = PortfolioService(upstox=UpstoxService(base_url=settings.upstox_api_base_url))
    return await svc.get_holdings(session, token, settings.default_trading_mode)


@router.get("/positions")
async def get_positions(session: AsyncSession = Depends(get_session)):
    tm = TokenManager(encryption_key=_enc_key)
    token = await tm.get_read_token(session)
    svc = PortfolioService(upstox=UpstoxService(base_url=settings.upstox_api_base_url))
    return await svc.get_positions(session, token, settings.default_trading_mode)


@router.get("/margins")
async def get_margins(session: AsyncSession = Depends(get_session)):
    tm = TokenManager(encryption_key=_enc_key)
    token = await tm.get_read_token(session)
    svc = PortfolioService(upstox=UpstoxService(base_url=settings.upstox_api_base_url))
    return await svc.get_margins(session, token, settings.default_trading_mode)
