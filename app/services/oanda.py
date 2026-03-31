from datetime import datetime

import httpx

TIMEFRAME_MAP = {
    "1m": "M1",
    "5m": "M5",
    "15m": "M15",
    "1h": "H1",
    "4h": "H4",
    "1D": "D",
    "M1": "M1",
    "M5": "M5",
    "M15": "M15",
    "H1": "H1",
    "H4": "H4",
    "D": "D",
}


class OandaService:
    def __init__(self, api_key: str, account_id: str, api_url: str):
        self._account_id = account_id
        self._api_url = api_url
        self._client = httpx.AsyncClient(
            base_url=api_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    def _map_timeframe(self, timeframe: str) -> str:
        return TIMEFRAME_MAP.get(timeframe, timeframe)

    async def fetch_candles(
        self,
        symbol: str,
        timeframe: str,
        count: int = 100,
    ) -> list[dict]:
        granularity = self._map_timeframe(timeframe)
        response = await self._client.get(
            f"/v3/instruments/{symbol}/candles",
            params={
                "granularity": granularity,
                "count": count,
                "price": "M",
            },
        )
        response.raise_for_status()
        data = response.json()

        candles = []
        for c in data.get("candles", []):
            if not c.get("complete", False):
                continue
            mid = c["mid"]
            candles.append(
                {
                    "symbol": data["instrument"],
                    "timeframe": timeframe,
                    "timestamp": datetime.fromisoformat(
                        c["time"].replace("000Z", "+00:00")
                    ),
                    "open": float(mid["o"]),
                    "high": float(mid["h"]),
                    "low": float(mid["l"]),
                    "close": float(mid["c"]),
                    "volume": int(c.get("volume", 0)),
                }
            )
        return candles

    async def close(self):
        await self._client.aclose()
