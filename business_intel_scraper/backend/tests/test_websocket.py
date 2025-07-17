from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[3]))
from business_intel_scraper.backend.api.notifications import ConnectionManager

manager = ConnectionManager()
app = FastAPI()


@app.websocket("/ws/notifications")
async def notifications(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


def test_websocket_echo() -> None:
    client = TestClient(app)
    with client.websocket_connect("/ws/notifications") as websocket:
        websocket.send_text("hello")
        data = websocket.receive_text()
        assert data == "hello"


def test_broadcast_to_multiple_clients() -> None:
    """Messages from one client should be broadcast to all connected clients."""

    client = TestClient(app)
    with client.websocket_connect("/ws/notifications") as ws1:
        with client.websocket_connect("/ws/notifications") as ws2:
            # Send a message from the first client
            ws1.send_text("greetings")
            # Both clients should receive the broadcast message
            assert ws1.receive_text() == "greetings"
            assert ws2.receive_text() == "greetings"

            # Send another message from the second client
            ws2.send_text("salutations")
            assert ws1.receive_text() == "salutations"
            assert ws2.receive_text() == "salutations"


def test_disconnect_handled_gracefully() -> None:
    """Server continues broadcasting when a client disconnects unexpectedly."""

    client = TestClient(app)
    with client.websocket_connect("/ws/notifications") as ws1:
        with client.websocket_connect("/ws/notifications") as ws2:
            ws1.send_text("first")
            assert ws1.receive_text() == "first"
            assert ws2.receive_text() == "first"

            # Close the first client unexpectedly
            ws1.close()

            # After disconnect the manager should only have one active connection
            assert len(manager.active_connections) == 1

            # Ensure the remaining client still receives broadcasts
            ws2.send_text("second")
            assert ws2.receive_text() == "second"
