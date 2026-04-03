import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Candle
from app.services.oanda import OandaService

logger = logging.getLogger(__name__)


class CandleIngestor:
    def __init__(self, oanda: OandaService):
        self._oanda = oanda

    async def ingest_once(
        self, session: AsyncSession, symbol: str, timeframe: str, count: int = 200
    ) -> int:
        raw_candles = await self._oanda.fetch_candles(symbol, timeframe, count=count)
        for c in raw_candles:
            existing = await session.execute(
                select(Candle).where(
                    Candle.symbol == c["symbol"],
                    Candle.timeframe == c["timeframe"],
                    Candle.timestamp == c["timestamp"],
                )
            )
            if existing.scalar_one_or_none() is not None:
                continue
            session.add(Candle(**c))
        await session.commit()
        return len(raw_candles)

    async def run_cycle(self, session_factory, symbols: list[str], timeframes: list[str]) -> None:
        for symbol in symbols:
            for timeframe in timeframes:
                try:
                    async with session_factory() as session:
                        count = await self.ingest_once(session, symbol, timeframe)
                        logger.info(f"Ingested {count} candles for {symbol}/{timeframe}")
                except Exception as e:
                    logger.error(f"Ingestion failed for {symbol}/{timeframe}: {e}")

    async def start(
        self,
        session_factory,
        symbols: list[str],
        timeframes: list[str],
        interval: int = 60,
    ) -> None:
        logger.info(f"Starting candle ingestor: {symbols} / {timeframes} every {interval}s")
        while True:
            await self.run_cycle(session_factory, symbols, timeframes)
            await asyncio.sleep(interval)
