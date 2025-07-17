"""Main FastAPI application entry point."""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
import asyncio
from pathlib import Path

from .rate_limit import RateLimitMiddleware

from .notifications import ConnectionManager

try:
    from sse_starlette.sse import EventSourceResponse
except Exception:  # pragma: no cover - optional dependency
    EventSourceResponse = StreamingResponse  # type: ignore

from ..workers.tasks import get_task_status, launch_scraping_task

from business_intel_scraper.settings import settings
from business_intel_scraper.backend.utils.helpers import LOG_FILE

app = FastAPI(title="Business Intelligence Scraper")
app.add_middleware(RateLimitMiddleware)

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

