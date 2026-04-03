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

# Note: candle ingestion removed — rebuilt in SP2 with Upstox

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    ws_manager = ConnectionManager()
    set_manager(ws_manager)
    app.state.ws_manager = ws_manager

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
