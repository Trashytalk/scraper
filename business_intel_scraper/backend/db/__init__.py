"""Database engine setup for the backend."""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base


DATABASE_URL = "sqlite:///./data.db"

# Create the SQLAlchemy engine. ``future=True`` enables 2.0 style usage.
engine = create_engine(DATABASE_URL, future=True, echo=False)

# Factory for database sessions used throughout the application.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    """Create all database tables if they do not exist."""

    Base.metadata.create_all(bind=engine)

