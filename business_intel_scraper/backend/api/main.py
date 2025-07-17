"""Main FastAPI application entry point."""

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
from .schemas import (
    HealthCheckResponse,
    TaskCreateResponse,
    TaskStatusResponse,
    JobStatus,
)
from ..workers.tasks import get_task_status, launch_scraping_task
from ..utils.helpers import LOG_FILE

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
# Track job status information in memory
jobs: dict[str, str] = {}


@app.get("/", response_model=HealthCheckResponse)
async def root() -> HealthCheckResponse:
    """Health check endpoint."""

    return HealthCheckResponse(
        message="API is running",
        database_url=settings.database.url,
    )


@app.post("/scrape", response_model=TaskCreateResponse)
async def start_scrape() -> TaskCreateResponse:
    """Launch a background scraping task using the example spider."""

    task_id = launch_scraping_task()
    jobs[task_id] = "running"
    return TaskCreateResponse(task_id=task_id)


@app.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def task_status(task_id: str) -> TaskStatusResponse:
    """Return the current status of a scraping task."""

    status = get_task_status(task_id)
    jobs[task_id] = status
    return TaskStatusResponse(status=status)


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


@app.get("/logs/stream")
async def stream_logs() -> EventSourceResponse:
    """Stream log file updates using Server-Sent Events."""

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


@app.get("/jobs", response_model=dict[str, JobStatus])
async def get_jobs() -> dict[str, JobStatus]:
    """Return job statuses."""

    return {jid: JobStatus(status=get_task_status(jid)) for jid in list(jobs)}


@app.get("/jobs/{job_id}", response_model=JobStatus)
async def get_job(job_id: str) -> JobStatus:
    """Return a single job status."""

    return JobStatus(status=jobs.get(job_id, "unknown"))
