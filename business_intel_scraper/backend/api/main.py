"""Main FastAPI application entry point."""

from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
    Depends,
    HTTPException,
    status,
)


from .notifications import ConnectionManager
from .rate_limit import RateLimitMiddleware
from ..workers.tasks import get_task_status, launch_scraping_task
from ..utils.helpers import LOG_FILE
from business_intel_scraper.settings import settings
from .rate_limit import RateLimitMiddleware

app = FastAPI(title="Business Intelligence Scraper")
app.add_middleware(RateLimitMiddleware)

manager = ConnectionManager()


@app.get("/")
async def root() -> dict[str, str]:
    """Health check endpoint."""
    return {"message": "API is running"}


@app.post("/scrape")
async def start_scrape() -> dict[str, str]:
    """Launch a background scraping task using the example spider."""
    task_id = launch_scraping_task()
    return {"task_id": task_id}


@app.get("/tasks/{task_id}")
async def task_status(task_id: str) -> dict[str, str]:
    """Return the current status of a scraping task."""
    status_ = get_task_status(task_id)
    return {"status": status_}


@app.websocket("/ws/notifications")
async def notifications(websocket: WebSocket) -> None:
    """Handle WebSocket connections for real-time notifications."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


