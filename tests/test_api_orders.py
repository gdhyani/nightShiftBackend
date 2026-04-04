async def test_place_paper_order(client):
    resp = await client.post("/api/orders", json={
        "symbol": "NSE_EQ|INE848E01016", "side": "BUY", "qty": 10,
        "order_type": "MARKET", "price": 2500.0,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["source"] == "paper"
    assert data["status"] == "filled"


async def test_calculate_charges(client):
    resp = await client.post("/api/charges/calculate", json={
        "symbol": "NSE_EQ|INE848E01016", "side": "BUY", "qty": 10, "price": 2500.0,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "total_charges" in data
    assert data["brokerage"] == 7.5
