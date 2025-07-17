from __future__ import annotations

import asyncio
from pathlib import Path
from typing import AsyncGenerator

import aiofiles
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from sse_starlette.sse import EventSourceResponse

from business_intel_scraper.settings import settings

from .notifications import ConnectionManager
from .rate_limit import RateLimitMiddleware
from ..utils.helpers import LOG_FILE
from ..workers.tasks import get_task_status, launch_scraping_task

app = FastAPI(title="Business Intelligence Scraper")

if settings.require_https:
    app.add_middleware(HTTPSRedirectMiddleware)

app.add_middleware(
    RateLimitMiddleware,
    limit=settings.rate_limit.limit,
    window=settings.rate_limit.window,
)

manager = ConnectionManager()

scraped_data: list[dict[str, str]] = []
jobs: dict[str, str] = {}


async def monitor_job(job_id: str) -> None:
    """Watch a background job and broadcast status changes."""
    previous = None
    while True:
        status = get_task_status(job_id)
        if status != previous:
            jobs[job_id] = status
            await manager.broadcast_json({"job_id": job_id, "status": status})
            previous = status
        if status in {"completed", "not_found"}:
            break
        await asyncio.sleep(1)


@app.get("/")
async def root() -> dict[str, str]:
    """Basic health check."""
    return {"message": "API is running", "database_url": settings.database.url}


@app.post("/scrape")
async def start_scrape() -> dict[str, str]:
    """Launch a background scraping task."""
    task_id = launch_scraping_task()
    jobs[task_id] = "running"
    asyncio.create_task(monitor_job(task_id))
    return {"task_id": task_id}


@app.get("/tasks/{task_id}")
async def task_status(task_id: str) -> dict[str, str]:
    """Return the current status of a scraping task."""
    status = get_task_status(task_id)
    jobs[task_id] = status
    return {"status": status}


@app.websocket("/ws/notifications")
async def notifications(websocket: WebSocket) -> None:
    """Handle WebSocket connections for real-time notifications."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive; ignore incoming messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/logs/stream")
async def stream_logs() -> EventSourceResponse:
    """Stream the application log file using SSE."""

    async def event_generator() -> AsyncGenerator[dict[str, str], None]:
        path = Path(LOG_FILE)
        path.touch(exist_ok=True)
        async with aiofiles.open(path, "r") as f:
            await f.seek(0, 2)
            while True:
                line = await f.readline()
                if line:
                    yield {"data": line.rstrip()}
                else:
                    await asyncio.sleep(0.5)

    return EventSourceResponse(event_generator())


@app.get("/data")
async def get_data() -> list[dict[str, str]]:
    """Return scraped data."""
    return scraped_data


@app.get("/jobs")
async def get_jobs() -> dict[str, dict[str, str]]:
    """Return job statuses."""
    return {jid: {"status": get_task_status(jid)} for jid in list(jobs)}


@app.get("/jobs/{job_id}")
async def get_job(job_id: str) -> dict[str, str]:
    """Return a single job status."""
    return jobs.get(job_id, {"status": "unknown"})
