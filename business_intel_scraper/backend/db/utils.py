from __future__ import annotations

from typing import Iterable, List

from .pipeline import normalize_names

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from .models import Base, Company

# Use an in-memory SQLite database by default
ENGINE = create_engine("sqlite:///:memory:", echo=False)
SessionLocal = sessionmaker(bind=ENGINE)


def init_db() -> None:
    """Create database tables."""
    Base.metadata.create_all(ENGINE)


def save_companies(names: Iterable[str]) -> List[Company]:
    """Persist unique company names to the database.

    Parameters
    ----------
    names : Iterable[str]
        Company names to persist.

    Returns
    -------
    list[Company]
        ORM objects that were inserted.
    """
    session = SessionLocal()
    cleaned_names = normalize_names(names)
    inserted: List[Company] = []
    for name in cleaned_names:
        exists = session.scalar(select(Company).where(Company.name == name))
        if not exists:
            company = Company(name=name)
            session.add(company)
            inserted.append(company)
    session.commit()
    session.close()
    return inserted
