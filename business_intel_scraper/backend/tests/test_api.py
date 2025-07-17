# ruff: noqa: E402
import os
import sys
import jwt
import pytest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
)

api = pytest.importorskip("business_intel_scraper.backend.api.main")
from fastapi.testclient import TestClient

app = api.app


def test_launch_and_check_task():
    secret = "secret"
    os.environ["JWT_SECRET"] = secret
    os.environ["JWT_ALGORITHM"] = "HS256"
    jwt.encode({"sub": "user"}, secret, algorithm="HS256")

    client = TestClient(app)

    resp = client.post("/scrape")
    assert resp.status_code == 200
    task_id = resp.json()["task_id"]
    assert isinstance(task_id, str)

    status_resp = client.get(f"/tasks/{task_id}")
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] in {"running", "completed"}


def test_nlp_process(monkeypatch):
    client = TestClient(app)

    monkeypatch.setattr(api.pipeline, "preprocess", lambda texts: texts)
    monkeypatch.setattr(api.pipeline, "extract_entities", lambda texts: ["A", "B"])

    resp = client.post("/nlp/process", json={"text": "dummy"})
    assert resp.status_code == 200
    assert resp.json() == {"entities": ["A", "B"]}
