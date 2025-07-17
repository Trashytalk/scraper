from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[3]))
from business_intel_scraper.backend.api.main import app


def test_websocket_echo() -> None:
    client = TestClient(app)
    with client.websocket_connect("/ws/notifications") as websocket:
        websocket.send_text("hello")
        data = websocket.receive_text()
        assert data == "hello"
