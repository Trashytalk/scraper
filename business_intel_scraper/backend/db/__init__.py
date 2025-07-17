"""Database utilities and session management."""

from __future__ import annotations

from business_intel_scraper.config import settings

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(settings.database_url, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Yield a database session."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
