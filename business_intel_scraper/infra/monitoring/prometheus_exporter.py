"""Prometheus metrics exporter for the BI Scraper platform."""

from __future__ import annotations

import random
import time

from prometheus_client import Gauge, Counter, start_http_server

REQUESTS_TOTAL = Counter(
    "bi_requests_total",
    "Total number of processed scraping requests.",
)
LAST_SCRAPE_TIME = Gauge(
    "bi_last_scrape_timestamp",
    "Unix timestamp of the last successful scrape.",
)


def record_scrape() -> None:
    """Record a single scrape event."""
    REQUESTS_TOTAL.inc()
    LAST_SCRAPE_TIME.set_to_current_time()


def run_exporter(port: int = 8000) -> None:
    """Run the Prometheus exporter HTTP server."""
    start_http_server(port)
    while True:  # pragma: no cover - simple demonstration loop
        record_scrape()
        time.sleep(random.uniform(1, 5))


if __name__ == "__main__":  # pragma: no cover - manual execution
    run_exporter()
