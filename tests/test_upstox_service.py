from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.upstox import UpstoxService


@pytest.fixture
def upstox():
    return UpstoxService(base_url="https://api.upstox.com")


async def test_get_ltp(upstox):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "status": "success",
        "data": {"NSE_EQ|INE848E01016": {"last_price": 2460.50, "instrument_token": "NSE_EQ|INE848E01016"}},
    }
    mock_resp.raise_for_status = MagicMock()

    with patch.object(upstox._client, "get", new=AsyncMock(return_value=mock_resp)):
        result = await upstox.get_ltp(["NSE_EQ|INE848E01016"], token="test-token")

    assert "NSE_EQ|INE848E01016" in result
    assert result["NSE_EQ|INE848E01016"]["last_price"] == 2460.50


async def test_exchange_auth_code(upstox):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"access_token": "new-daily-token", "token_type": "Bearer", "expires_in": 86400}
    mock_resp.raise_for_status = MagicMock()

    with patch.object(upstox._client, "post", new=AsyncMock(return_value=mock_resp)):
        result = await upstox.exchange_auth_code(
            code="auth-code-123", client_id="test-id", client_secret="test-secret",
            redirect_uri="http://localhost/callback",
        )

    assert result["access_token"] == "new-daily-token"


async def test_request_daily_token(upstox):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "status": "success",
        "data": {"authorization_expiry": "1732226400000", "notifier_url": "https://example.com/webhook"},
    }
    mock_resp.raise_for_status = MagicMock()

    with patch.object(upstox._client, "post", new=AsyncMock(return_value=mock_resp)):
        result = await upstox.request_daily_token(client_id="test-id", client_secret="test-secret")

    assert result["status"] == "success"
