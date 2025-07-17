"""Main FastAPI application entry point."""

import asyncio
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from sse_starlette.sse import EventSourceResponse

from .notifications import ConnectionManager
from .rate_limit import RateLimitMiddleware
from ..utils.helpers import LOG_FILE

from ..workers.tasks import get_task_status, launch_scraping_task

from business_intel_scraper.settings import settings

app = FastAPI(title="Business Intelligence Scraper")
if settings.require_https:
    app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    limit=settings.rate_limit.limit,
    window=settings.rate_limit.window,
)

manager = ConnectionManager()


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
    return {"message": "API is running"}


@app.post("/scrape")
async def start_scrape() -> dict[str, str]:
    """Launch a background scraping task using the example spider."""

    task_id = launch_scraping_task()
    return {"task_id": task_id}


@app.get("/tasks/{task_id}")
async def task_status(task_id: str) -> dict[str, str]:
    """Return the current status of a scraping task."""

    status = get_task_status(task_id)
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
    return jobs


@app.get("/jobs/{job_id}")
async def get_job(job_id: str) -> dict[str, str]:
    """Return a single job status."""
    return jobs.get(job_id, {"status": "unknown"})

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
