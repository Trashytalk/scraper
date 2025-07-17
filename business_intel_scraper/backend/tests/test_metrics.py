# ruff: noqa: E402
import os
import sys
import pytest

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")),
)
api = pytest.importorskip("business_intel_scraper.backend.api.main")
from fastapi.testclient import TestClient

app = api.app


def test_metrics_endpoint_exposes_prometheus() -> None:
    client = TestClient(app)
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "bi_requests_total" in resp.text
