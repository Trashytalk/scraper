from __future__ import annotations

from typing import Any, List

from fastapi import WebSocket


class ConnectionManager:
    """Manage active WebSocket connections."""

    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str) -> None:
        for connection in list(self.active_connections):
            await connection.send_text(message)

    async def broadcast_json(self, data: dict[str, Any]) -> None:
        """Send a JSON message to all connected clients."""
        for connection in list(self.active_connections):
            await connection.send_json(data)
