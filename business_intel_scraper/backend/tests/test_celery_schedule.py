import os
import sys
import pytest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
)

tasks = pytest.importorskip("business_intel_scraper.backend.workers.tasks")


def test_periodic_task_registered() -> None:
    assert "example_spider_hourly" in tasks.celery_app.conf.beat_schedule
    entry = tasks.celery_app.conf.beat_schedule["example_spider_hourly"]
    assert (
        entry["task"]
        == "business_intel_scraper.backend.workers.tasks.scheduled_example_scrape"
    )
