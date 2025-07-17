"""Main FastAPI application entry point."""

from fastapi import FastAPI
from sse_starlette.sse import EventSourceResponse
import asyncio
from pathlib import Path

from ..utils.helpers import setup_logging, LOG_FILE

setup_logging()

app = FastAPI(title="Business Intelligence Scraper")


@app.get("/")
async def root() -> dict[str, str]:
    """Health check endpoint.

    Returns
    -------
    dict[str, str]
        A simple message confirming the service is running.
    """
    return {"message": "API is running"}


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
