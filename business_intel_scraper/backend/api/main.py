"""Main FastAPI application entry point."""

from fastapi import FastAPI

# Simple in-memory placeholders. In a real application these would come from a
# database or task queue.
scraped_data: list[dict[str, str]] = [
    {"id": "1", "url": "https://example.com"},
]

jobs: dict[str, dict[str, str]] = {
    "example": {"status": "completed"},
}

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
