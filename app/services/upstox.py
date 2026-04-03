import logging

import httpx

logger = logging.getLogger(__name__)


class UpstoxService:
    def __init__(self, base_url: str = "https://api.upstox.com"):
        self._base_url = base_url
        self._client = httpx.AsyncClient(base_url=base_url, timeout=30.0)

    def _auth_headers(self, token: str) -> dict:
        return {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    async def get_ltp(self, instrument_keys: list[str], token: str) -> dict:
        keys_param = ",".join(instrument_keys)
        resp = await self._client.get(
            "/v3/market-quote/ltp",
            params={"instrument_key": keys_param},
            headers=self._auth_headers(token),
        )
        resp.raise_for_status()
        return resp.json().get("data", {})

    async def get_full_quote(self, instrument_keys: list[str], token: str) -> dict:
        keys_param = ",".join(instrument_keys)
        resp = await self._client.get(
            "/v2/market-quote/quotes",
            params={"instrument_key": keys_param},
            headers=self._auth_headers(token),
        )
        resp.raise_for_status()
        return resp.json().get("data", {})

    async def exchange_auth_code(
        self, code: str, client_id: str, client_secret: str, redirect_uri: str
    ) -> dict:
        resp = await self._client.post(
            "/v2/login/authorization/token",
            data={
                "code": code, "client_id": client_id, "client_secret": client_secret,
                "redirect_uri": redirect_uri, "grant_type": "authorization_code",
            },
            headers={"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"},
        )
        resp.raise_for_status()
        return resp.json()

    async def request_daily_token(self, client_id: str, client_secret: str) -> dict:
        resp = await self._client.post(
            f"/v3/login/auth/token/request/{client_id}",
            json={"client_secret": client_secret},
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )
        resp.raise_for_status()
        return resp.json()

    async def close(self):
        await self._client.aclose()
