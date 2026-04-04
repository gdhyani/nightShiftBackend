import logging

from app.services.upstox import UpstoxService

logger = logging.getLogger(__name__)


class UpstoxOrderService:
    def __init__(self, upstox: UpstoxService):
        self._upstox = upstox

    async def place_order(self, token, symbol, side, qty,
                         order_type="MARKET", price=0,
                         trigger_price=0, product="D") -> dict:
        resp = await self._upstox._client.post(
            "/v3/order/place",
            json={"quantity": qty, "product": product, "validity": "DAY",
                  "price": price, "tag": "nightshift",
                  "instrument_token": symbol, "order_type": order_type,
                  "transaction_type": side, "disclosed_quantity": 0,
                  "trigger_price": trigger_price, "is_amo": False},
            headers=self._upstox._auth_headers(token),
        )
        resp.raise_for_status()
        return resp.json()

    async def modify_order(self, token, order_id, qty=None,
                          price=None, trigger_price=None) -> dict:
        body = {"order_id": order_id}
        if qty is not None:
            body["quantity"] = qty
        if price is not None:
            body["price"] = price
        if trigger_price is not None:
            body["trigger_price"] = trigger_price
        resp = await self._upstox._client.put(
            "/v3/order/modify", json=body,
            headers=self._upstox._auth_headers(token),
        )
        resp.raise_for_status()
        return resp.json()

    async def cancel_order(self, token, order_id) -> dict:
        resp = await self._upstox._client.delete(
            "/v2/order/cancel", params={"order_id": order_id},
            headers=self._upstox._auth_headers(token),
        )
        resp.raise_for_status()
        return resp.json()

    async def get_order_book(self, token) -> list:
        resp = await self._upstox._client.get(
            "/v2/order/retrieve-all",
            headers=self._upstox._auth_headers(token),
        )
        resp.raise_for_status()
        return resp.json().get("data", [])

    async def get_order_details(self, token, order_id) -> dict:
        resp = await self._upstox._client.get(
            "/v2/order/history", params={"order_id": order_id},
            headers=self._upstox._auth_headers(token),
        )
        resp.raise_for_status()
        return resp.json().get("data", {})
