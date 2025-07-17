"""Main FastAPI application entry point."""

from fastapi import FastAPI

from ..workers.tasks import get_task_status, launch_scraping_task

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
