"""Repository classes for database access."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .models import Base, Company

# Create a simple SQLite engine for demonstration purposes
ENGINE = create_engine("sqlite:///business_intel.db", echo=False)
SessionLocal = sessionmaker(bind=ENGINE)


def init_db() -> None:
    """Initialize database tables."""
    Base.metadata.create_all(bind=ENGINE)


class CompanyRepository:
    """Repository for :class:`~.models.Company` objects."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, name: str) -> Company:
        """Persist a new company record."""
        company = Company(name=name)
        self._session.add(company)
        self._session.commit()
        self._session.refresh(company)
        return company

    def get(self, company_id: int) -> Optional[Company]:
        """Retrieve a company by primary key."""
        return self._session.get(Company, company_id)

    def list(self) -> list[Company]:
        """Return all companies."""
        stmt = self._session.query(Company)
        return list(stmt.all())

    def delete(self, company_id: int) -> None:
        """Delete a company record."""
        company = self.get(company_id)
        if company is not None:
            self._session.delete(company)
            self._session.commit()
