import ssl
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


def _build_engine_url():
    """Normalize DATABASE_URL for asyncpg compatibility."""
    url = settings.database_url
    # Ensure asyncpg driver prefix
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    # Remove sslmode param (asyncpg uses connect_args instead)
    url = url.replace("?sslmode=require", "").replace("&sslmode=require", "")
    return url


def _build_connect_args():
    """Build SSL connect args if using a remote database."""
    if "leapcell" in settings.database_url or "sslmode=require" in settings.database_url:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        return {"ssl": ssl_context}
    return {}


engine = create_async_engine(
    _build_engine_url(),
    echo=settings.debug,
    connect_args=_build_connect_args(),
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
