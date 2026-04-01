import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.ws_manager import ConnectionManager

logger = logging.getLogger(__name__)

router = APIRouter()

manager: ConnectionManager | None = None


def set_manager(mgr: ConnectionManager) -> None:
    global manager
    manager = mgr


def get_manager() -> ConnectionManager:
    assert manager is not None, "WebSocket manager not initialized"
    return manager


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    mgr = get_manager()
    channels = ["price_ticks", "store_updated"]

    await mgr.connect(websocket, channels)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if "subscribe" in msg:
                    mgr.resubscribe(websocket, msg["subscribe"])
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        mgr.disconnect(websocket)
