"""Main FastAPI application entry point."""

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from sse_starlette.sse import EventSourceResponse
from pathlib import Path
import asyncio

from .notifications import ConnectionManager
from .rate_limit import RateLimitMiddleware
from ..workers.tasks import get_task_status, launch_scraping_task
from ..db.models import Company
from ..db.repository import SessionLocal
from sqlalchemy.orm import Session
from typing import Generator
from sqlalchemy import select
from pydantic import BaseModel

from business_intel_scraper.settings import settings

app = FastAPI(title="Business Intelligence Scraper")
app.add_middleware(RateLimitMiddleware)

manager = ConnectionManager()

# Simple in-memory stores used by a few demonstration endpoints
scraped_data: list[dict[str, str]] = []
jobs: dict[str, str] = {}


def get_db() -> Generator[Session, None, None]:
    """Provide a database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class CompanyCreate(BaseModel):
    name: str


class CompanyRead(BaseModel):
    id: int
    name: str


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

    async def event_generator():
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

@app.post("/companies", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
def create_company(company: CompanyCreate, db: Session = Depends(get_db)) -> Company:
    """Create a new ``Company`` record."""

    db_company = Company(name=company.name)
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


@app.get("/companies/{company_id}", response_model=CompanyRead)
def read_company(company_id: int, db: Session = Depends(get_db)) -> Company:
    """Retrieve a ``Company`` by ID."""

    stmt = select(Company).where(Company.id == company_id)
    result = db.execute(stmt).scalar_one_or_none()
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    return result


@app.get("/companies", response_model=list[CompanyRead])
def list_companies(db: Session = Depends(get_db)) -> list[Company]:
    """List all ``Company`` records."""

    stmt = select(Company)
    return list(db.execute(stmt).scalars())
