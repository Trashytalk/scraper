"""SQLAlchemy models."""

from __future__ import annotations

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for ORM models."""

    pass


class Company(Base):
    """ORM model for a company."""

    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    tasks: Mapped[list["ScrapeTask"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )


class Location(Base):
    """ORM model for a geocoded location."""

    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    address: Mapped[str] = mapped_column(String, nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(nullable=False)
    longitude: Mapped[float] = mapped_column(nullable=False)



class User(Base):
    """ORM model for an authenticated user."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    # Relationship to tasks omitted to keep test models lightweight


class ScrapeTask(Base):
    """ORM model for a scraping task."""

    __tablename__ = "scrape_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    company_id: Mapped[int | None] = mapped_column(
        ForeignKey("companies.id"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(String, default="pending")
    company: Mapped[Company | None] = relationship(back_populates="tasks")


class OsintResult(Base):
    """ORM model for OSINT results produced by a task."""

    __tablename__ = "osint_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("scrape_tasks.id"), index=True)
    data: Mapped[str] = mapped_column(String, nullable=False)
    # Relationship omitted
