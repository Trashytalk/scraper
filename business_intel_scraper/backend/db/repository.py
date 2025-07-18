"""Repository classes for database access."""

from __future__ import annotations

from typing import Optional
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .models import (
    Base,
    Company,
    Location,
    OsintResult,
    ScrapeTask,
    User,
    Article,
)

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


class ArticleRepository:
    """Repository for :class:`~.models.Article` objects."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, title: str, url: str, published: datetime | None = None) -> Article:
        """Persist a new article record."""
        article = Article(title=title, url=url, published=published)
        self._session.add(article)
        self._session.commit()
        self._session.refresh(article)
        return article

    def list(self) -> list[Article]:
        stmt = self._session.query(Article)
        return list(stmt.all())


# ---------------------------------------------------------------------------
# CRUD helper functions
# ---------------------------------------------------------------------------


def create_company(session: Session, name: str) -> Company:
    """Create and persist a :class:`Company`."""

    company = Company(name=name)
    session.add(company)
    session.commit()
    session.refresh(company)
    return company


def get_company(session: Session, company_id: int) -> Optional[Company]:
    """Return a company by primary key."""

    return session.get(Company, company_id)


def update_company(
    session: Session, company_id: int, **fields: object
) -> Optional[Company]:
    """Update a company record and return the updated instance."""

    company = get_company(session, company_id)
    if company is None:
        return None
    for key, value in fields.items():
        setattr(company, key, value)
    session.commit()
    session.refresh(company)
    return company


def delete_company(session: Session, company_id: int) -> bool:
    """Delete a company and return ``True`` if it existed."""

    company = get_company(session, company_id)
    if company is None:
        return False
    session.delete(company)
    session.commit()
    return True


def create_location(
    session: Session, address: str, latitude: float, longitude: float
) -> Location:
    """Insert a new :class:`Location`."""

    location = Location(address=address, latitude=latitude, longitude=longitude)
    session.add(location)
    session.commit()
    session.refresh(location)
    return location


def get_location(session: Session, location_id: int) -> Optional[Location]:
    """Return a location by primary key."""

    return session.get(Location, location_id)


def update_location(
    session: Session, location_id: int, **fields: object
) -> Optional[Location]:
    """Update a location record."""

    location = get_location(session, location_id)
    if location is None:
        return None
    for key, value in fields.items():
        setattr(location, key, value)
    session.commit()
    session.refresh(location)
    return location


def delete_location(session: Session, location_id: int) -> bool:
    """Delete a location and return ``True`` if it existed."""

    location = get_location(session, location_id)
    if location is None:
        return False
    session.delete(location)
    session.commit()
    return True


def create_user(session: Session, username: str, hashed_password: str) -> User:
    """Create a :class:`User`."""

    user = User(username=username, hashed_password=hashed_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_user(session: Session, user_id: int) -> Optional[User]:
    """Retrieve a user by primary key."""

    return session.get(User, user_id)


def update_user(session: Session, user_id: int, **fields: object) -> Optional[User]:
    """Update a user record."""

    user = get_user(session, user_id)
    if user is None:
        return None
    for key, value in fields.items():
        setattr(user, key, value)
    session.commit()
    session.refresh(user)
    return user


def delete_user(session: Session, user_id: int) -> bool:
    """Delete a user and return ``True`` if it existed."""

    user = get_user(session, user_id)
    if user is None:
        return False
    session.delete(user)
    session.commit()
    return True


def create_task(
    session: Session,
    user_id: int,
    company_id: int | None = None,
    status: str = "pending",
) -> ScrapeTask:
    """Insert a new :class:`ScrapeTask`."""

    task = ScrapeTask(user_id=user_id, company_id=company_id, status=status)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def get_task(session: Session, task_id: int) -> Optional[ScrapeTask]:
    """Return a task by primary key."""

    return session.get(ScrapeTask, task_id)


def update_task(
    session: Session, task_id: int, **fields: object
) -> Optional[ScrapeTask]:
    """Update a task record."""

    task = get_task(session, task_id)
    if task is None:
        return None
    for key, value in fields.items():
        setattr(task, key, value)
    session.commit()
    session.refresh(task)
    return task


def delete_task(session: Session, task_id: int) -> bool:
    """Delete a task and return ``True`` if it existed."""

    task = get_task(session, task_id)
    if task is None:
        return False
    session.delete(task)
    session.commit()
    return True


def create_result(session: Session, task_id: int, data: str) -> OsintResult:
    """Insert an :class:`OsintResult`."""

    result = OsintResult(task_id=task_id, data=data)
    session.add(result)
    session.commit()
    session.refresh(result)
    return result


def get_result(session: Session, result_id: int) -> Optional[OsintResult]:
    """Return an OSINT result by primary key."""

    return session.get(OsintResult, result_id)


def update_result(
    session: Session, result_id: int, **fields: object
) -> Optional[OsintResult]:
    """Update an OSINT result record."""

    result = get_result(session, result_id)
    if result is None:
        return None
    for key, value in fields.items():
        setattr(result, key, value)
    session.commit()
    session.refresh(result)
    return result


def delete_result(session: Session, result_id: int) -> bool:
    """Delete an OSINT result and return ``True`` if it existed."""

    result = get_result(session, result_id)
    if result is None:
        return False
    session.delete(result)
    session.commit()
    return True


def create_article(
    session: Session, title: str, url: str, published: datetime | None = None
) -> Article:
    """Insert a new :class:`Article`."""

    article = Article(title=title, url=url, published=published)
    session.add(article)
    session.commit()
    session.refresh(article)
    return article


def list_articles(session: Session) -> list[Article]:
    """Return all :class:`Article` records."""

    stmt = session.query(Article)
    return list(stmt.all())
