from collections.abc import AsyncGenerator
from datetime import datetime, timezone

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_session
from app.main import create_app
from app.models import Candle

TEST_DB_URL = "sqlite+aiosqlite:///./test.db"

test_engine = create_async_engine(TEST_DB_URL, echo=False)
test_session_factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    app = create_app()

    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
def sample_candles() -> list[dict]:
    base = datetime(2026, 3, 30, 10, 0, 0, tzinfo=timezone.utc)
    prices = [
        (1.0800, 1.0850, 1.0780, 1.0840, 1000),
        (1.0840, 1.0870, 1.0820, 1.0860, 1200),
        (1.0860, 1.0900, 1.0850, 1.0880, 900),
        (1.0880, 1.0890, 1.0830, 1.0835, 1100),
        (1.0835, 1.0860, 1.0810, 1.0850, 950),
    ]
    candles = []
    for i, (o, h, l, c, v) in enumerate(prices):
        candles.append({
            "symbol": "EUR_USD",
            "timeframe": "H1",
            "timestamp": base.replace(hour=10 + i),
            "open": o,
            "high": h,
            "low": l,
            "close": c,
            "volume": v,
        })
    return candles
