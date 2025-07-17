"""Example unit tests."""

from __future__ import annotations

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

tasks = pytest.importorskip("business_intel_scraper.backend.workers.tasks")
example_task = tasks.example_task


def test_example_task() -> None:
    """Ensure example_task adds two numbers."""
    assert example_task(1, 2) == 3
