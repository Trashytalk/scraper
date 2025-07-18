from __future__ import annotations

import os
import sys

import pytest
from fastapi.testclient import TestClient

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")

api = pytest.importorskip("business_intel_scraper.backend.api.main")
app = api.app


def test_query_scraped_data() -> None:
    client = TestClient(app)
    resp = client.post("/graphql", json={"query": "{ scrapedData }"})
    assert resp.status_code == 200
    assert resp.json()["data"]["scrapedData"] == []
