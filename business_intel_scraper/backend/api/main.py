"""Main FastAPI application entry point."""

from fastapi import FastAPI
from sse_starlette.sse import EventSourceResponse
import asyncio
from pathlib import Path

from ..utils.helpers import setup_logging, LOG_FILE

setup_logging()
from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from ..db.models import Base, Company

# --- Database setup -----------------------------------------------------
engine = create_engine(
    "sqlite:///./app.db", connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Provide a SQLAlchemy session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Pydantic schemas ---------------------------------------------------

class CompanyCreate(BaseModel):
    """Schema for creating companies."""

    name: str


class CompanyRead(BaseModel):
    """Schema for reading companies."""

    id: int
    name: str

    class Config:
        orm_mode = True


# Simple in-memory placeholders. In a real application these would come from a
# database or task queue.
scraped_data: list[dict[str, str]] = [
    {"id": "1", "url": "https://example.com"},
]

jobs: dict[str, dict[str, str]] = {
    "example": {"status": "completed"},
}

from .rate_limit import RateLimitMiddleware

app = FastAPI(title="Business Intelligence Scraper")
app.add_middleware(RateLimitMiddleware)


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
