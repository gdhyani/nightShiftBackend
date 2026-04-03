import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.candle_ingestor import CandleIngestor
from app.services.store_updater import StoreUpdater
from app.services.upstox import UpstoxService

logger = logging.getLogger(__name__)


class UpstoxIngestor:
    def __init__(
        self,
        upstox: UpstoxService,
        candle_ingestor: CandleIngestor,
        store_updater: StoreUpdater,
    ):
        self._upstox = upstox
        self._candle_ingestor = candle_ingestor
        self._store_updater = store_updater

    @staticmethod
    def map_timeframe(tf: str) -> tuple[str, int]:
        mapping = {
            "1": ("minutes", 1),
            "5": ("minutes", 5),
            "15": ("minutes", 15),
            "60": ("minutes", 60),
            "day": ("days", 1),
        }
        if tf in mapping:
            return mapping[tf]
        return ("minutes", int(tf))

    async def ingest_symbol(
        self,
        session: AsyncSession,
        symbol: str,
        timeframe: str,
        token: str,
    ) -> int:
        unit, interval = self.map_timeframe(timeframe)
        now = datetime.now(timezone.utc)
        from_date = (now - timedelta(days=7)).strftime("%Y-%m-%d")
        to_date = now.strftime("%Y-%m-%d")

        candles = await self._upstox.get_historical_candles(
            instrument_key=symbol,
            unit=unit,
            interval=interval,
            from_date=from_date,
            to_date=to_date,
            token=token,
        )

        inserted = await self._candle_ingestor.ingest_candles(session, candles)
        await self._store_updater.update_snapshot(session, symbol, f"{unit}_{interval}")
        return inserted

    async def run_cycle(
        self,
        session_factory,
        symbols: list[str],
        timeframes: list[str],
        token: str,
        ws_manager=None,
    ):
        for symbol in symbols:
            for timeframe in timeframes:
                try:
                    async with session_factory() as session:
                        count = await self.ingest_symbol(session, symbol, timeframe, token)
                        logger.info(f"Ingested {count} candles for {symbol}/{timeframe}")
                        if ws_manager:
                            await ws_manager.broadcast(
                                {"type": "candle_update", "symbol": symbol, "timeframe": timeframe}
                            )
                except Exception:
                    logger.exception(f"Error ingesting {symbol}/{timeframe}")
                await asyncio.sleep(0.2)

    async def start(
        self,
        session_factory,
        symbols: list[str],
        timeframes: list[str],
        token_manager,
        interval: float,
        ws_manager=None,
    ):
        while True:
            token = token_manager.get_read_token()
            if not token:
                logger.warning("No Upstox read token available, skipping cycle")
            else:
                await self.run_cycle(session_factory, symbols, timeframes, token, ws_manager)
            await asyncio.sleep(interval)
