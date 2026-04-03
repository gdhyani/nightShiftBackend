async def test_get_market_quote_no_token(client):
    resp = await client.get("/api/market/quote/NSE_EQ%7CINE848E01016")
    assert resp.status_code == 200
    data = resp.json()
    assert "error" in data or "status" in data


async def test_get_historical_candles_no_token(client):
    resp = await client.get(
        "/api/market/candles/NSE_EQ%7CINE848E01016"
        "?unit=minutes&interval=5&from_date=2026-01-01&to_date=2026-01-02"
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "error" in data or isinstance(data, list)
