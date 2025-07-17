from __future__ import annotations

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from sse_starlette.sse import EventSourceResponse
from pathlib import Path
import asyncio
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from .notifications import ConnectionManager
from .rate_limit import RateLimitMiddleware
from ..workers.tasks import get_task_status, launch_scraping_task
from ..security import require_token
from ..utils.helpers import LOG_FILE
from business_intel_scraper.settings import settings
from ..db.models import Company, Location
from ..db import SessionLocal
from .auth import router as auth_router

from pydantic import BaseModel
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
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "same-origin")
        return response


app.add_middleware(SecurityHeadersMiddleware)

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

@app.get("/")
async def root() -> dict[str, str]:
    """Basic health check."""
    return {"message": "API is running", "database_url": settings.database.url}

@app.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def task_status(task_id: str) -> TaskStatusResponse:

@app.post("/scrape/start")
async def enqueue_scrape() -> dict[str, str]:
    """Enqueue a new scraping task."""

@app.post("/scrape")
async def start_scrape(token: str = Depends(require_token)) -> dict[str, str]:
    """Launch a background scraping task using the example spider."""


@app.get("/tasks/{task_id}")
async def task_status(task_id: str) -> dict[str, str]:
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


@app.websocket("/logs/stream")
async def stream_logs_ws(websocket: WebSocket) -> None:
    """Stream log file updates over a WebSocket connection."""
    await websocket.accept()
    path = Path(LOG_FILE)
    path.touch(exist_ok=True)
    async with aiofiles.open(path, "r") as f:
        await f.seek(0, 2)
        try:
            while True:
                line = await f.readline()
                if line:
                    await websocket.send_text(line.rstrip())
                else:
                    await asyncio.sleep(0.5)
        except WebSocketDisconnect:
            pass

@app.get("/data")
async def get_data() -> list[dict[str, str]]:
    """Return scraped data."""

    return scraped_data


@app.get("/jobs", dependencies=[require_role(UserRole.ADMIN)])
async def get_jobs() -> dict[str, dict[str, str]]:

    """Return job statuses."""

    return {jid: JobStatus(status=get_task_status(jid)) for jid in list(jobs)}

@app.get("/jobs/{job_id}", dependencies=[require_role(UserRole.ADMIN)])
async def get_job(job_id: str) -> dict[str, str]:

    """Return a single job status."""
    return jobs.get(job_id, {"status": "unknown"})


@app.get("/locations/{company_id}")
def get_locations(company_id: int, db: Session = Depends(get_db)) -> list[dict[str, object]]:
    """Return stored location data for a company."""
    locations = db.execute(select(Location)).scalars().all()
    return [
        {
            "id": loc.id,
            "address": loc.address,
            "latitude": loc.latitude,
            "longitude": loc.longitude,
        }
        for loc in locations
    ]
