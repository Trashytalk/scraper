# ruff: noqa: E402
import os
import sys
import jwt
from business_intel_scraper.backend.security import create_token
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
    token = create_token("1", "analyst")

    client = TestClient(app)
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/scrape", headers=headers)
    assert resp.status_code == 200
    task_id = resp.json()["task_id"]
    assert isinstance(task_id, str)

    status_resp = client.get(f"/tasks/{task_id}", headers=headers)
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] in {"running", "completed"}


def test_nlp_process(monkeypatch):
    token = create_token("1", "analyst")
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {token}"}

    monkeypatch.setattr(api.pipeline, "preprocess", lambda texts: texts)
    monkeypatch.setattr(api.pipeline, "extract_entities", lambda texts: ["A", "B"])

    resp = client.post("/nlp/process", json={"text": "dummy"}, headers=headers)
    assert resp.status_code == 200
    assert resp.json() == {"entities": ["A", "B"]}
