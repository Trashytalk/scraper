import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

api = pytest.importorskip("business_intel_scraper.backend.api.main")
from fastapi.testclient import TestClient

app = api.app


def test_launch_and_check_task():
    client = TestClient(app)

    resp = client.post('/scrape/start')
    assert resp.status_code == 200
    task_id = resp.json()['task_id']
    assert isinstance(task_id, str)

    status_resp = client.get(f'/scrape/status/{task_id}')
    assert status_resp.status_code == 200
    assert status_resp.json()['status'] in {'running', 'completed'}
