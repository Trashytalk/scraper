"""Main FastAPI application entry point."""

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
from ..utils.helpers import LOG_FILE
from business_intel_scraper.settings import settings
from ..db.models import Company
from ..db import SessionLocal
from pydantic import BaseModel
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
from sse_starlette.sse import EventSourceResponse

from sqlalchemy.orm import Session
from sqlalchemy import select


from .notifications import ConnectionManager
from .rate_limit import RateLimitMiddleware

try:
    from sse_starlette.sse import EventSourceResponse
except Exception:  # pragma: no cover - optional dependency
    EventSourceResponse = StreamingResponse  # type: ignore

try:
    from sse_starlette.sse import EventSourceResponse
except Exception:  # pragma: no cover - optional dependency
    EventSourceResponse = StreamingResponse  # type: ignore

from .rate_limit import RateLimitMiddleware

from ..workers.tasks import get_task_status, launch_scraping_task

from sse_starlette.sse import EventSourceResponse
import asyncio
from pathlib import Path
import aiofiles
from business_intel_scraper.settings import settings
from business_intel_scraper.backend.utils.helpers import LOG_FILE


from ..db.models import Company
from ..db import get_db
from ..utils.helpers import LOG_FILE

from pydantic import BaseModel


class CompanyCreate(BaseModel):
    name: str


class CompanyRead(BaseModel):
    id: int
    name: str


app = FastAPI(title="Business Intelligence Scraper")
if settings.require_https:
    app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    limit=settings.rate_limit.limit,
    window=settings.rate_limit.window,
)
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
jobs: dict[str, dict[str, str]] = {}


class CompanyCreate(BaseModel):
    name: str


class CompanyRead(BaseModel):
    id: int
    name: str


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root() -> dict[str, str]:
    """Health check endpoint.

    Returns
    -------
    dict[str, str]
        A simple message confirming the service is running.
    """
    return {
        "message": "API is running",
        "database_url": settings.database.url,
    }


@app.post("/scrape")
async def start_scrape() -> dict[str, str]:
    """Launch a background scraping task using the example spider."""
    task_id = launch_scraping_task()
    jobs[task_id] = "running"
    return {"task_id": task_id}


@app.get("/tasks/{task_id}")
async def task_status(task_id: str) -> dict[str, str]:
    """Return the current status of a scraping task."""
    status_ = get_task_status(task_id)
    return {"status": status_}

    status = get_task_status(task_id)
    jobs[task_id] = status
    return {"status": status}


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


@app.get("/jobs")
async def get_jobs() -> dict[str, dict[str, str]]:
    """Return job statuses."""
    return {jid: {"status": get_task_status(jid)} for jid in list(jobs)}


@app.get("/jobs/{job_id}")
async def get_job(job_id: str) -> dict[str, str]:
    """Return a single job status."""
    return jobs.get(job_id, {"status": "unknown"})
