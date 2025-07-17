"""Main FastAPI application entry point."""

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
