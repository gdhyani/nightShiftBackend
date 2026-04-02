import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.agents import router as agents_router
from app.api.candles import router as candles_router
from app.api.indicators import router as indicators_router
from app.api.store import router as store_router
from app.api.ws import router as ws_router, set_manager
from app.core.config import settings
from app.core.database import async_session, engine
from app.core.ws_manager import ConnectionManager
from app.services.candle_ingestor import CandleIngestor
from app.services.oanda import OandaService
from app.services.store_calculator import StoreCalculator
from app.services.store_updater import StoreUpdater

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    ws_manager = ConnectionManager()
    set_manager(ws_manager)
    app.state.ws_manager = ws_manager

    ingest_task = None
    if settings.oanda_api_key:
        oanda = OandaService(
            api_key=settings.oanda_api_key,
            account_id=settings.oanda_account_id,
            api_url=settings.oanda_api_url,
        )
        ingestor = CandleIngestor(oanda=oanda)
        calculator = StoreCalculator()
        updater = StoreUpdater(calculator=calculator)

        async def ingest_and_update_loop():
            while True:
                try:
                    for symbol in settings.watchlist_symbols:
                        for tf in settings.timeframes_list:
                            async with async_session() as session:
                                await ingestor.ingest_once(session, symbol, tf)
                            async with async_session() as session:
                                indicators = await updater.update_snapshot(session, symbol, tf)
                            if indicators:
                                await ws_manager.broadcast("store_updated", {
                                    "channel": "store_updated",
                                    "symbol": symbol,
                                    "timeframe": tf,
                                    "data": indicators,
                                })
                except Exception as e:
                    logger.error(f"Ingestion cycle error: {e}")
                await asyncio.sleep(settings.ingest_interval)

        ingest_task = asyncio.create_task(ingest_and_update_loop())
        logger.info("Background ingestion started")

    agent_runner = None
    if settings.llm_api_key:
        from app.services.agent_runner import AgentRunner
        agent_runner = AgentRunner(session_factory=async_session, ws_manager=ws_manager)
        agent_runner.start_all()
        logger.info("Agent runner started")

    yield

    # Shutdown
    if agent_runner:
        agent_runner.stop_all()
    if ingest_task:
        ingest_task.cancel()
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title="NightShift API",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(agents_router)
    app.include_router(candles_router)
    app.include_router(store_router)
    app.include_router(indicators_router)
    app.include_router(ws_router)

    return app


app = create_app()


@app.get("/health")
async def health():
    return {"status": "ok"}
