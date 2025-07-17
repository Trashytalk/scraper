import os
import sys
import pytest

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")),
)

# Import tasks module and function
tasks = pytest.importorskip("business_intel_scraper.backend.workers.tasks")
run_spider_task = tasks.run_spider_task


def test_run_spider_task_html() -> None:
    """Run the example spider on provided HTML."""
    items = run_spider_task("example", html="<html></html>")
    assert items == [{"url": "https://example.com"}]
