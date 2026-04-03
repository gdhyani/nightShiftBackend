import pytest

from app.models.instrument import Instrument
from app.services.instrument_service import InstrumentService


@pytest.fixture
async def seeded_session(db_session):
    instruments = [
        Instrument(
            instrument_key="NSE_EQ|INE002A01018",
            symbol="RELIANCE",
            name="Reliance Industries Limited",
            exchange="NSE",
            segment="EQ",
        ),
        Instrument(
            instrument_key="NSE_EQ|INE040A01034",
            symbol="HDFCBANK",
            name="HDFC Bank Limited",
            exchange="NSE",
            segment="EQ",
        ),
        Instrument(
            instrument_key="NSE_EQ|INE467B01029",
            symbol="TCS",
            name="Tata Consultancy Services Limited",
            exchange="NSE",
            segment="EQ",
        ),
    ]
    for inst in instruments:
        db_session.add(inst)
    await db_session.flush()
    return db_session


@pytest.fixture
def service():
    return InstrumentService()


async def test_search_by_symbol(seeded_session, service):
    results = await service.search(seeded_session, "REL")
    assert len(results) >= 1
    symbols = [r.symbol for r in results]
    assert "RELIANCE" in symbols


async def test_search_by_name(seeded_session, service):
    results = await service.search(seeded_session, "HDFC")
    assert len(results) >= 1
    symbols = [r.symbol for r in results]
    assert "HDFCBANK" in symbols


async def test_get_by_key(seeded_session, service):
    result = await service.get_by_key(seeded_session, "NSE_EQ|INE467B01029")
    assert result is not None
    assert result.symbol == "TCS"


async def test_get_by_key_not_found(seeded_session, service):
    result = await service.get_by_key(seeded_session, "NSE_EQ|INVALID")
    assert result is None
