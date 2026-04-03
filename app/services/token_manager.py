import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserTradingConfig
from app.utils.encryption import decrypt_token, encrypt_token

logger = logging.getLogger(__name__)


class TokenManager:
    def __init__(self, encryption_key: str):
        self._key = encryption_key

    async def get_or_create_config(
        self, session: AsyncSession, user_id: str = "default"
    ) -> UserTradingConfig:
        result = await session.execute(
            select(UserTradingConfig).where(
                UserTradingConfig.user_id == user_id
            )
        )
        config = result.scalar_one_or_none()
        if config is None:
            config = UserTradingConfig(user_id=user_id)
            session.add(config)
            await session.commit()
            await session.refresh(config)
        return config

    def _is_token_valid(self, token_enc: str, expires_at: datetime | None) -> bool:
        if not token_enc:
            return False
        if expires_at is None:
            return False
        now = datetime.now(timezone.utc)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return now < expires_at

    async def get_read_token(
        self, session: AsyncSession, user_id: str = "default"
    ) -> str | None:
        config = await self.get_or_create_config(session, user_id)
        if self._is_token_valid(config.daily_token_enc, config.daily_token_expires_at):
            return decrypt_token(config.daily_token_enc, self._key)
        return None

    async def get_write_token(
        self, session: AsyncSession, user_id: str = "default", mode: str | None = None
    ) -> tuple[str | None, str]:
        config = await self.get_or_create_config(session, user_id)
        effective_mode = mode or config.default_mode

        if effective_mode == "paper":
            if self._is_token_valid(config.sandbox_token_enc, config.sandbox_token_expires_at):
                return decrypt_token(config.sandbox_token_enc, self._key), "paper"
            return None, "awaiting_auth"

        if self._is_token_valid(config.daily_token_enc, config.daily_token_expires_at):
            return decrypt_token(config.daily_token_enc, self._key), "live"
        return None, "awaiting_auth"

    async def store_daily_token(
        self, session: AsyncSession, user_id: str, token: str, expires_at: datetime
    ) -> None:
        config = await self.get_or_create_config(session, user_id)
        config.daily_token_enc = encrypt_token(token, self._key)
        config.daily_token_expires_at = expires_at
        config.updated_at = datetime.now(timezone.utc)
        await session.commit()

    async def store_sandbox_token(
        self, session: AsyncSession, user_id: str, token: str, expires_at: datetime
    ) -> None:
        config = await self.get_or_create_config(session, user_id)
        config.sandbox_token_enc = encrypt_token(token, self._key)
        config.sandbox_token_expires_at = expires_at
        config.updated_at = datetime.now(timezone.utc)
        await session.commit()

    async def get_token_status(
        self, session: AsyncSession, user_id: str = "default"
    ) -> dict:
        config = await self.get_or_create_config(session, user_id)

        def status(enc: str, exp: datetime | None) -> str:
            if not enc:
                return "missing"
            if exp is None:
                return "missing"
            now = datetime.now(timezone.utc)
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            return "active" if now < exp else "expired"

        return {
            "daily": status(config.daily_token_enc, config.daily_token_expires_at),
            "sandbox": status(config.sandbox_token_enc, config.sandbox_token_expires_at),
            "mode": config.default_mode,
            "client_id_set": bool(config.upstox_client_id),
        }
