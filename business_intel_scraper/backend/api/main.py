from __future__ import annotations

import asyncio
from pathlib import Path
from typing import AsyncGenerator

import aiofiles
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from sse_starlette.sse import EventSourceResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from .metrics import MetricsMiddleware, metrics_app
from pydantic import BaseModel

from business_intel_scraper.settings import settings

from .auth import router as auth_router
from .dependencies import require_role
from .notifications import ConnectionManager
from .rate_limit import RateLimitMiddleware
from .schemas import (
    HealthCheckResponse,
    JobStatus,
    TaskCreateResponse,
    TaskStatusResponse,
)
from ..db.models import UserRole
from ..nlp import pipeline
from ..utils.helpers import LOG_FILE
from ..workers.tasks import get_task_status, launch_scraping_task


class NLPRequest(BaseModel):
    text: str


class NLPResponse(BaseModel):
    entities: list[str]


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
app.add_middleware(MetricsMiddleware)
app.mount("/metrics", metrics_app)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "same-origin")
        return response


app.add_middleware(SecurityHeadersMiddleware)
manager = ConnectionManager()

# Track scraped data and job status in memory
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


@app.get("/", response_model=HealthCheckResponse)
async def root() -> HealthCheckResponse:
    """Basic health check."""

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


@app.get("/jobs", dependencies=[require_role(UserRole.ADMIN)])
async def get_jobs() -> dict[str, JobStatus]:
    """Return job statuses."""

    return {jid: JobStatus(status=get_task_status(jid)) for jid in list(jobs)}


@app.get("/jobs/{job_id}", dependencies=[require_role(UserRole.ADMIN)])
async def get_job(job_id: str) -> dict[str, str]:
    """Return a single job status."""

    return jobs.get(job_id, {"status": "unknown"})


@app.post("/nlp/process")
async def process_text(payload: NLPRequest) -> NLPResponse:
    """Extract entities from provided text."""

    cleaned = pipeline.preprocess([payload.text])
    entities = pipeline.extract_entities(cleaned)
    return NLPResponse(entities=entities)
