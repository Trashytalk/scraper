from __future__ import annotations

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from sse_starlette.sse import EventSourceResponse
from pathlib import Path
import asyncio
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from business_intel_scraper.infra.monitoring.prometheus_exporter import record_scrape

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
async def start_scrape() -> dict[str, str]:
    """Launch a background scraping task."""
    task_id = launch_scraping_task()
    jobs[task_id] = "running"
    asyncio.create_task(monitor_job(task_id))
    """
    This simply wraps :func:`launch_scraping_task` from ``workers.tasks`` and
    stores the task identifier in the in-memory ``jobs`` registry so it can be
    queried later.
    """
    task_id = launch_scraping_task()
    jobs[task_id] = "running"
    record_scrape()
    return {"task_id": task_id}


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
    return jobs.get(job_id, {"status": "unknown"})


@app.get("/metrics")
async def metrics() -> Response:
    """Expose Prometheus metrics for scraping."""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    return JobStatus(status=jobs.get(job_id, "unknown"))

@app.post(
    "/companies/", response_model=CompanyRead, status_code=status.HTTP_201_CREATED
)
async def create_company(
    company: CompanyCreate, db: Session = Depends(get_db)
) -> Company:
    """Create a new company."""
    db_company = Company(name=company.name)
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


@app.get("/companies/{company_id}", response_model=CompanyRead)
async def read_company(company_id: int, db: Session = Depends(get_db)) -> Company:
    """Retrieve a company by ID."""
    db_company = db.get(Company, company_id)
    if not db_company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )
    return db_company


@app.delete("/companies/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(company_id: int, db: Session = Depends(get_db)) -> Response:
    """Delete a company by ID."""
    db_company = db.get(Company, company_id)
    if not db_company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Company not found"
        )
    db.delete(db_company)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
