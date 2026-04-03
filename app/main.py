import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.account import router as account_router
from app.api.agents import router as agents_router
from app.api.analytics import router as analytics_router
from app.api.auth import router as auth_router
from app.api.candles import router as candles_router
from app.api.indicators import router as indicators_router
from app.api.instruments import router as instruments_router
from app.api.market import router as market_router
from app.api.reports import router as reports_router
from app.api.skills_api import router as skills_router
from app.api.store import router as store_router
from app.api.strategies import router as strategies_router
from app.api.trades import router as trades_router
from app.api.ws import router as ws_router
from app.api.ws import set_manager
from app.core.config import settings
from app.core.database import async_session, engine
from app.core.ws_manager import ConnectionManager
from app.services.candle_ingestor import CandleIngestor
from app.services.store_calculator import StoreCalculator
from app.services.store_updater import StoreUpdater
from app.services.token_manager import TokenManager
from app.services.upstox import UpstoxService
from app.services.upstox_ingestor import UpstoxIngestor
from app.utils.encryption import generate_key

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    ws_manager = ConnectionManager()
    set_manager(ws_manager)
    app.state.ws_manager = ws_manager

    _enc_key = settings.token_encryption_key or generate_key()
    ingest_task = None
    if settings.upstox_client_id:
        upstox_svc = UpstoxService(base_url=settings.upstox_api_base_url)
        candle_ingestor = CandleIngestor()
        calculator = StoreCalculator()
        store_updater = StoreUpdater(calculator=calculator)
        upstox_ingestor = UpstoxIngestor(
            upstox=upstox_svc, candle_ingestor=candle_ingestor,
            store_updater=store_updater,
        )
        tm = TokenManager(encryption_key=_enc_key)

        async def _ingest_loop():
            await upstox_ingestor.start(
                session_factory=async_session,
                symbols=settings.watchlist_symbols,
                timeframes=settings.timeframes_list,
                token_manager=tm,
                interval=settings.ingest_interval,
                ws_manager=ws_manager,
            )

        ingest_task = asyncio.create_task(_ingest_loop())
        logger.info("Upstox candle ingestion started")

    agent_runner = None
    if settings.llm_api_key:
        from app.services.agent_runner import AgentRunner
        agent_runner = AgentRunner(session_factory=async_session, ws_manager=ws_manager)
        agent_runner.start_all()
        logger.info("Agent runner started")

    strategy_runner_svc = None
    if settings.llm_api_key:
        from app.services.strategy_runner import StrategyRunner as StratRunner
        strategy_runner_svc = StratRunner(session_factory=async_session, ws_manager=ws_manager)
        try:
            await strategy_runner_svc.start_strategies()
            logger.info("Strategy runner started")
        except Exception as e:
            logger.error(f"Strategy runner failed to start (will retry in loops): {e}")

    yield

    # Shutdown
    if ingest_task:
        ingest_task.cancel()
    if strategy_runner_svc:
        strategy_runner_svc.stop_all()
    if agent_runner:
        agent_runner.stop_all()
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

    app.include_router(account_router)
    app.include_router(auth_router)
    app.include_router(agents_router)
    app.include_router(analytics_router)
    app.include_router(candles_router)
    app.include_router(indicators_router)
    app.include_router(instruments_router)
    app.include_router(market_router)
    app.include_router(reports_router)
    app.include_router(skills_router)
    app.include_router(store_router)
    app.include_router(strategies_router)
    app.include_router(trades_router)
    app.include_router(ws_router)

    return app


app = create_app()


@app.get("/health")
async def health():
    return {"status": "ok"}
