import logging

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self._connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channels: list[str]) -> None:
        await websocket.accept()
        self._subscribe(websocket, channels)

    def _subscribe(self, websocket: WebSocket, channels: list[str]) -> None:
        for channel in channels:
            if channel not in self._connections:
                self._connections[channel] = []
            self._connections[channel].append(websocket)
        logger.info(f"WebSocket subscribed to: {channels}")

    def resubscribe(self, websocket: WebSocket, channels: list[str]) -> None:
        self.disconnect(websocket)
        self._subscribe(websocket, channels)

    def disconnect(self, websocket: WebSocket) -> None:
        for channel, connections in self._connections.items():
            if websocket in connections:
                connections.remove(websocket)
        logger.info("WebSocket disconnected")

    async def broadcast(self, channel: str, data: dict) -> None:
        connections = self._connections.get(channel, [])
        dead = []
        for ws in connections:
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

    async def send_personal(self, websocket: WebSocket, data: dict) -> None:
        await websocket.send_json(data)
