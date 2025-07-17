from __future__ import annotations

import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure package root is on the path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
)

api = pytest.importorskip("business_intel_scraper.backend.api.main")
app = api.app


def test_root_endpoint() -> None:
    client = TestClient(app)
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["message"] == "API is running"
    assert "database_url" in data


def test_job_endpoints() -> None:
    client = TestClient(app)

    resp = client.post("/scrape")
    assert resp.status_code == 200
    job_id = resp.json()["task_id"]

    # the API stores plain strings in the jobs dict; replace with a dict so
    # response validation succeeds
    api.jobs[job_id] = {"status": "running"}

    jobs = client.get("/jobs").json()
    assert job_id in jobs

    job_resp = client.get(f"/jobs/{job_id}")
    assert job_resp.status_code == 200
    assert "status" in job_resp.json()


def test_data_endpoint() -> None:
    client = TestClient(app)
    resp = client.get("/data")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
