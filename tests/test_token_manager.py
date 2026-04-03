from datetime import datetime, timedelta, timezone

import pytest

from app.models import UserTradingConfig
from app.services.token_manager import TokenManager
from app.utils.encryption import generate_key, encrypt_token


@pytest.fixture
def enc_key():
    return generate_key()


@pytest.fixture
async def seeded_config(db_session, enc_key):
    now = datetime.now(timezone.utc)
    config = UserTradingConfig(
        user_id="test_user",
        upstox_client_id="test-client",
        daily_token_enc=encrypt_token("daily-tok-123", enc_key),
        daily_token_expires_at=now + timedelta(hours=8),
        sandbox_token_enc=encrypt_token("sandbox-tok-456", enc_key),
        sandbox_token_expires_at=now + timedelta(days=25),
        default_mode="paper",
    )
    db_session.add(config)
    await db_session.commit()
    return config


async def test_get_read_token_returns_daily(db_session, seeded_config, enc_key):
    tm = TokenManager(encryption_key=enc_key)
    token = await tm.get_read_token(db_session, "test_user")
    assert token == "daily-tok-123"


async def test_get_read_token_expired_returns_none(db_session, enc_key):
    now = datetime.now(timezone.utc)
    config = UserTradingConfig(
        user_id="expired_user",
        daily_token_enc=encrypt_token("old-tok", enc_key),
        daily_token_expires_at=now - timedelta(hours=1),
        default_mode="paper",
    )
    db_session.add(config)
    await db_session.commit()
    tm = TokenManager(encryption_key=enc_key)
    token = await tm.get_read_token(db_session, "expired_user")
    assert token is None


async def test_get_write_token_paper_returns_sandbox(db_session, seeded_config, enc_key):
    tm = TokenManager(encryption_key=enc_key)
    token, mode = await tm.get_write_token(db_session, "test_user")
    assert token == "sandbox-tok-456"
    assert mode == "paper"


async def test_get_write_token_live_returns_daily(db_session, seeded_config, enc_key):
    tm = TokenManager(encryption_key=enc_key)
    token, mode = await tm.get_write_token(db_session, "test_user", mode="live")
    assert token == "daily-tok-123"
    assert mode == "live"


async def test_get_write_token_live_expired_returns_none(db_session, enc_key):
    now = datetime.now(timezone.utc)
    config = UserTradingConfig(
        user_id="expired_live",
        daily_token_enc=encrypt_token("old", enc_key),
        daily_token_expires_at=now - timedelta(hours=1),
        default_mode="live",
    )
    db_session.add(config)
    await db_session.commit()
    tm = TokenManager(encryption_key=enc_key)
    token, mode = await tm.get_write_token(db_session, "expired_live")
    assert token is None
    assert mode == "awaiting_auth"


async def test_get_token_status(db_session, seeded_config, enc_key):
    tm = TokenManager(encryption_key=enc_key)
    status = await tm.get_token_status(db_session, "test_user")
    assert status["daily"] == "active"
    assert status["sandbox"] == "active"
    assert status["mode"] == "paper"
