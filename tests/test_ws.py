from starlette.testclient import TestClient

from app.main import create_app


def test_websocket_connect():
    app = create_app()
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as ws:
            ws.send_json({"subscribe": ["price_ticks"]})
            # Connection accepted — no error


def test_websocket_invalid_message():
    app = create_app()
    with TestClient(app) as client:
        with client.websocket_connect("/ws") as ws:
            ws.send_text("not json")
            # Should not crash
