"""Unit tests for workers and database utilities."""

from __future__ import annotations

import os
import sys
import pytest
from business_intel_scraper.backend.db.utils import (
    Base,
    ENGINE,
    init_db,
    save_companies,
    SessionLocal,
)
from business_intel_scraper.backend.db.models import Company

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

tasks = pytest.importorskip("business_intel_scraper.backend.workers.tasks")
example_task = tasks.example_task

from business_intel_scraper.backend.db.utils import (
    Base,
    ENGINE,
    SessionLocal,
    init_db,
    save_companies,
)
from business_intel_scraper.backend.db.models import Company


def setup_function() -> None:
    """Reset the in-memory database before each test."""
    Base.metadata.drop_all(ENGINE)
    init_db()


def test_example_task() -> None:
    """Ensure example_task adds two numbers."""
    assert example_task(1, 2) == 3


def test_save_companies_deduplication() -> None:
    """Companies should be deduplicated before insertion."""
    names = ["Acme", "Beta", "Acme", "  Beta  ", "Gamma", ""]
    inserted = save_companies(names)
    session = SessionLocal()
    count = session.query(Company).count()
    session.close()

    assert len(inserted) == 3
    assert count == 3
