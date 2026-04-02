from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Candle, StoreSnapshot


async def read_candles(session: AsyncSession, symbol: str, timeframe: str, count: int = 100) -> str:
    result = await session.execute(
        select(Candle).where(Candle.symbol == symbol, Candle.timeframe == timeframe)
        .order_by(Candle.timestamp.desc()).limit(count)
    )
    candles = list(reversed(result.scalars().all()))
    if not candles:
        return f"No candles found for {symbol}/{timeframe}"
    lines = [f"Candles for {symbol}/{timeframe} (latest {len(candles)}):"]
    lines.append("timestamp | open | high | low | close | volume")
    for c in candles[-20:]:
        lines.append(f"{c.timestamp.isoformat()} | {c.open:.5f} | {c.high:.5f} | {c.low:.5f} | {c.close:.5f} | {c.volume:.0f}")
    return "\n".join(lines)


async def read_store(session: AsyncSession, symbol: str) -> dict:
    result = await session.execute(select(StoreSnapshot).where(StoreSnapshot.symbol == symbol))
    snapshot = result.scalar_one_or_none()
    if snapshot is None:
        return {"error": f"No store snapshot for {symbol}"}
    return snapshot.data
