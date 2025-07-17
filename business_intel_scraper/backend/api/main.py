"""Main FastAPI application entry point."""

from fastapi import FastAPI

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
