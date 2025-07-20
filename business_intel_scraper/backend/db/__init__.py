"""Database utilities and session management."""

from __future__ import annotations

from typing import Iterator

from settings import settings

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = settings.database.url

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Iterator[Session]:
    """Yield a database session."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
