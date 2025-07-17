"""Example unit tests."""

from __future__ import annotations

import pytest

tasks = pytest.importorskip("business_intel_scraper.backend.workers.tasks")
example_task = tasks.example_task


def test_example_task() -> None:
    """Ensure example_task adds two numbers."""
    assert example_task(1, 2) == 3
