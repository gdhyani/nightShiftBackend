import ssl
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


def _build_engine_url():
    """Normalize DATABASE_URL for asyncpg compatibility."""
    from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

    url = settings.database_url
    # Ensure asyncpg driver prefix
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    # Strip query params that asyncpg doesn't understand
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    params.pop("sslmode", None)
    params.pop("channel_binding", None)
    clean_query = urlencode(params, doseq=True)
    return urlunparse(parsed._replace(query=clean_query))


def _build_connect_args():
    """Build SSL connect args if using a remote database."""
    if any(k in settings.database_url for k in ("leapcell", "neon.tech", "sslmode=require")):
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        return {
            "ssl": ssl_context,
            "prepared_statement_cache_size": 0,
            "statement_cache_size": 0,
        }
    return {}


engine = create_async_engine(
    _build_engine_url(),
    echo=settings.debug,
    connect_args=_build_connect_args(),
    pool_pre_ping=True,
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
