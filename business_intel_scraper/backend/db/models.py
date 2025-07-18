"""SQLAlchemy models."""

from __future__ import annotations


from sqlalchemy import String, ForeignKey, DateTime
from datetime import datetime
from enum import Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class UserRole(str, Enum):
    """Available user roles."""

    ADMIN = "admin"
    ANALYST = "analyst"


class Base(DeclarativeBase):
    """Base class for ORM models."""

    pass


class Company(Base):
    """ORM model for a company."""

    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    location_id: Mapped[int | None] = mapped_column(
        ForeignKey("locations.id"),
        nullable=True,
        index=True,
    )
    location: Mapped["Location"] = relationship(
        back_populates="companies",
    )
    tasks: Mapped[list["ScrapeTask"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )


class Location(Base):
    """ORM model for a geocoded location."""

    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    address: Mapped[str] = mapped_column(String, nullable=False)
    latitude: Mapped[float] = mapped_column(nullable=False)
    longitude: Mapped[float] = mapped_column(nullable=False)
    companies: Mapped[list["Company"]] = relationship(
        back_populates="location",
        cascade="all, delete-orphan",
    )


class User(Base):
    """ORM model for an authenticated user."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(
        String, unique=True, nullable=False, index=True
    )

    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        String,
        nullable=False,
        default=UserRole.ANALYST,
    )
    # Relationship to tasks omitted to keep test models lightweight


class ScrapeTask(Base):
    """ORM model for a scraping task."""

    __tablename__ = "scrape_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    company_id: Mapped[int | None] = mapped_column(
        ForeignKey("companies.id"),
        nullable=True,
    )

    company: Mapped["Company"] = relationship("Company", back_populates="tasks")
    status: Mapped[str] = mapped_column(String, default="pending")


class OsintResult(Base):
    """ORM model for OSINT results produced by a task."""

    __tablename__ = "osint_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("scrape_tasks.id"))
    data: Mapped[str] = mapped_column(String, nullable=False)
    # Relationship omitted


class JobEvent(Base):
    """Record of job lifecycle events."""

    __tablename__ = "job_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    event: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str | None] = mapped_column(String, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Article(Base):
    """ORM model for a scraped news article."""

    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    published: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
