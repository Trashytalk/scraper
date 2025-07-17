"""Main FastAPI application entry point."""

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from sqlalchemy import select
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse

from pathlib import Path
import asyncio


from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from sse_starlette.sse import EventSourceResponse
import asyncio
from pathlib import Path
from .rate_limit import RateLimitMiddleware
from .notifications import ConnectionManager
from .rate_limit import RateLimitMiddleware
from .schemas import CompanyCreate, CompanyRead
from ..db.models import Company
from ..db.repository import SessionLocal, init_db
from ..workers.tasks import get_task_status, launch_scraping_task
from ..db.models import Company
from ..db.repository import SessionLocal
from sqlalchemy.orm import Session
from typing import Generator
from sqlalchemy import select
from pydantic import BaseModel
from .notifications import ConnectionManager
from .rate_limit import RateLimitMiddleware
from ..workers.tasks import get_task_status, launch_scraping_task
from ..utils.helpers import LOG_FILE
from business_intel_scraper.settings import settings
from ..utils.helpers import LOG_FILE
from pydantic import BaseModel


class CompanyCreate(BaseModel):
    """Pydantic model for creating a company."""

    name: str


class CompanyRead(BaseModel):
    """Pydantic model representing a company record."""

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

manager = ConnectionManager()

LOG_FILE = "backend.log"
scraped_data: list[dict[str, str]] = []
jobs: dict[str, dict[str, str]] = {}

init_db()


def get_db() -> Session:
    """Provide a database session for request handling."""

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
        with path.open() as f:
            f.seek(0, 2)
            while True:
                line = f.readline()
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
    status = get_task_status(job_id)
    jobs[job_id] = status
    return {"status": status}
