from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.testclient import TestClient

from app.api.ws import router as ws_router, set_manager
from app.core.ws_manager import ConnectionManager


def _create_test_ws_app() -> FastAPI:
    """Create a minimal app with just the WS endpoint for testing."""

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        mgr = ConnectionManager()
        set_manager(mgr)
        yield

    app = FastAPI(lifespan=lifespan)
    app.include_router(ws_router)
    return app


def test_websocket_connect():
    app = _create_test_ws_app()
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as ws:
            ws.send_json({"subscribe": ["price_ticks"]})


def test_websocket_invalid_message():
    app = _create_test_ws_app()
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as ws:
            ws.send_text("not json")
