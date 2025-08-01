from __future__ import annotations

import asyncio
from pathlib import Path
from typing import AsyncGenerator, Callable, Awaitable

import aiofiles
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from sse_starlette.sse import EventSourceResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from .metrics import MetricsMiddleware, metrics_app
from pydantic import BaseModel

from business_intel_scraper.settings import settings
from ..utils import setup_request_cache
from .auth import router as auth_router
from .analytics import router as analytics_router
from .jobs import router as jobs_router
from .osint import router as osint_router
from .centralized_data import router as centralized_data_router
from ..analytics.middleware import AnalyticsMiddleware
from fastapi import Depends
from ..security import require_token, require_role
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
from ..utils import export
from ..workers.tasks import get_task_status, launch_scraping_task

setup_request_cache()


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

# Include analytics router
app.include_router(analytics_router)

# Include jobs router
app.include_router(jobs_router)

# Include OSINT router
app.include_router(osint_router)

# Include centralized data router
app.include_router(centralized_data_router)

# Include performance router
try:
    from .performance import router as performance_router

    app.include_router(performance_router)
except ImportError as e:
    print(f"Warning: Could not import performance router: {e}")

# Include marketplace router
try:
    from ..marketplace.api import router as marketplace_router

    app.include_router(marketplace_router)
except ImportError as e:
    print(f"Warning: Could not import marketplace router: {e}")

# Include AI router
try:
    from ..ai.api import router as ai_router

    app.include_router(ai_router)
except ImportError as e:
    print(f"Warning: Could not import AI router: {e}")

# Include storage router
try:
    from ..storage.api import router as storage_router

    app.include_router(storage_router, prefix="/api/v1")
except ImportError as e:
    print(f"Warning: Could not import storage router: {e}")

# Include visualization router
try:
    from .visualization import router as visualization_router

    app.include_router(visualization_router, prefix="/api/v1")
except ImportError as e:
    print(f"Warning: Could not import visualization router: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(AnalyticsMiddleware)
app.add_middleware(MetricsMiddleware)
app.mount("/metrics", metrics_app)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
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

from .graphql import graphql_app  # noqa: E402

app.include_router(graphql_app, prefix="/graphql")


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


@app.post(
    "/scrape", response_model=TaskCreateResponse, dependencies=[Depends(require_token)]
)
async def start_scrape() -> TaskCreateResponse:
    """Launch a background scraping task using the example spider."""

    task_id = launch_scraping_task()
    jobs[task_id] = "running"
    return TaskCreateResponse(task_id=task_id)


@app.get(
    "/tasks/{task_id}",
    response_model=TaskStatusResponse,
    dependencies=[Depends(require_token)],
)
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


@app.get("/logs/stream", dependencies=[Depends(require_token)])
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


@app.get("/data", dependencies=[Depends(require_token)])
async def get_data() -> list[dict[str, str]]:
    """Return scraped data."""

    return scraped_data


@app.get("/export", dependencies=[Depends(require_token)], response_model=None)
async def export_data(
    format: str = "jsonl", bucket: str | None = None, key: str | None = None
):
    """Export scraped data in the requested format."""

    if format == "csv":
        text = export.to_csv(scraped_data)
        return Response(text, media_type="text/csv")
    if format == "jsonl":
        text = export.to_jsonl(scraped_data)
        return Response(text, media_type="application/json")
    if format == "s3":
        if not bucket or not key:
            raise HTTPException(status_code=400, detail="bucket and key required")
        try:
            location = export.upload_to_s3(scraped_data, bucket, key)
        except Exception as exc:  # pragma: no cover - external service errors
            raise HTTPException(status_code=500, detail=str(exc))
        return {"location": location}
    raise HTTPException(status_code=400, detail="unsupported format")


@app.get(
    "/jobs",
    dependencies=[Depends(require_token), require_role(UserRole.ADMIN)],
)
async def get_jobs() -> dict[str, JobStatus]:
    """Return job statuses."""

    return {jid: JobStatus(status=get_task_status(jid)) for jid in list(jobs)}


@app.get(
    "/jobs/{job_id}",
    dependencies=[Depends(require_token), require_role(UserRole.ADMIN)],
)
async def get_job(job_id: str) -> dict[str, str]:
    """Return a single job status."""

    result = jobs.get(job_id, {"status": "unknown"})
    return result if isinstance(result, dict) else {"status": str(result)}


@app.post("/nlp/process", dependencies=[Depends(require_token)])
async def process_text(payload: NLPRequest) -> NLPResponse:
    """Extract entities from provided text."""

    cleaned = pipeline.preprocess([payload.text])
    entities = pipeline.extract_entities(cleaned)
    return NLPResponse(entities=entities)
