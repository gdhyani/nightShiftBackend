from datetime import datetime, timedelta, timezone

import pytest

from app.models import UserTradingConfig
from app.utils.encryption import encrypt_token, generate_key


@pytest.fixture
async def seeded_trading_config(db_session):
    key = generate_key()
    now = datetime.now(timezone.utc)
    config = UserTradingConfig(
        user_id="default",
        upstox_client_id="test-client",
        daily_token_enc=encrypt_token("daily-token", key),
        daily_token_expires_at=now + timedelta(hours=8),
        sandbox_token_enc=encrypt_token("sandbox-token", key),
        sandbox_token_expires_at=now + timedelta(days=25),
        default_mode="paper",
    )
    db_session.add(config)
    await db_session.commit()
    return config


async def test_get_trading_config(client, seeded_trading_config):
    resp = await client.get("/api/trading/config")
    assert resp.status_code == 200
    data = resp.json()
    assert data["mode"] == "paper"
    assert "daily" in data
    assert "sandbox" in data


async def test_switch_trading_mode(client, seeded_trading_config):
    resp = await client.put("/api/trading/mode", json={"mode": "live"})
    assert resp.status_code == 200
    assert resp.json()["mode"] == "live"


async def test_get_auth_status(client, seeded_trading_config):
    resp = await client.get("/api/auth/upstox/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "daily" in data


async def test_webhook_receives_token(client):
    resp = await client.post(
        "/api/webhooks/upstox/token",
        json={
            "client_id": "test", "user_id": "default",
            "access_token": "new-daily-token", "token_type": "Bearer",
            "expires_at": str(int((datetime.now(timezone.utc) + timedelta(hours=8)).timestamp() * 1000)),
            "message_type": "access_token",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
