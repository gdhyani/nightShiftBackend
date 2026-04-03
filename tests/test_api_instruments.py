import pytest
from app.models import Instrument


@pytest.fixture
async def seeded_instruments_api(db_session):
    for symbol, key, name in [
        ("RELIANCE", "NSE_EQ|INE002A01018", "Reliance Industries"),
        ("HDFCBANK", "NSE_EQ|INE040A01034", "HDFC Bank Ltd"),
        ("TCS", "NSE_EQ|INE467B01029", "Tata Consultancy"),
    ]:
        db_session.add(Instrument(
            instrument_key=key, symbol=symbol, name=name,
            exchange="NSE", segment="EQ",
        ))
    await db_session.commit()


async def test_search_instruments(client, seeded_instruments_api):
    resp = await client.get("/api/instruments/search?q=REL")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["symbol"] == "RELIANCE"


async def test_get_instrument(client, seeded_instruments_api):
    resp = await client.get("/api/instruments/NSE_EQ|INE002A01018")
    assert resp.status_code == 200
    assert resp.json()["symbol"] == "RELIANCE"


async def test_get_instrument_not_found(client):
    resp = await client.get("/api/instruments/INVALID")
    assert resp.status_code == 404
