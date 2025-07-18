import os
import time
import json
import shutil
import subprocess
from pathlib import Path
import sys

# ruff: noqa: E402

import pytest
import requests

ROOT = Path(__file__).resolve().parents[4]
COMPOSE_FILE = ROOT / "business_intel_scraper" / "docker-compose.yml"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from business_intel_scraper.backend.security import create_token


def _docker_available() -> bool:
    """Return True if docker and docker-compose are installed."""
    return (
        shutil.which("docker") is not None
        and shutil.which("docker-compose") is not None
    )


@pytest.fixture(scope="module")
def services():
    """Spin up API and Celery worker using docker-compose."""
    if not _docker_available():
        pytest.skip("Docker Compose not available")

    env = os.environ.copy()
    env.setdefault("CELERY_BROKER_URL", "memory://")
    env.setdefault("CELERY_RESULT_BACKEND", "cache+memory://")

    subprocess.run(
        [
            "docker-compose",
            "-f",
            str(COMPOSE_FILE),
            "up",
            "-d",
            "--build",
        ],
        check=True,
        cwd=ROOT,
        env=env,
    )

    # Wait for the API container to be reachable
    for _ in range(30):
        try:
            r = requests.get("http://localhost:8000/")
            if r.status_code == 200:
                break
        except Exception:
            time.sleep(1)
    else:
        subprocess.run(
            [
                "docker-compose",
                "-f",
                str(COMPOSE_FILE),
                "logs",
            ],
            cwd=ROOT,
            env=env,
        )
        pytest.fail("API service did not start")

    yield env

    subprocess.run(
        [
            "docker-compose",
            "-f",
            str(COMPOSE_FILE),
            "down",
            "-v",
        ],
        check=False,
        cwd=ROOT,
        env=env,
    )


def test_api_celery_db_flow(services):
    """End-to-end test for API -> Celery -> DB."""
    env = services
    os.environ["JWT_SECRET"] = "secret"
    os.environ["JWT_ALGORITHM"] = "HS256"
    token = create_token("1", "analyst")
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.post("http://localhost:8000/scrape", headers=headers)
    assert resp.status_code == 200
    task_id = resp.json()["task_id"]

    status = "running"
    for _ in range(40):
        r = requests.get(f"http://localhost:8000/tasks/{task_id}", headers=headers)
        assert r.status_code == 200
        status = r.json()["status"]
        if status == "completed":
            break
        time.sleep(0.5)

    assert status == "completed"

    cmd = [
        "docker-compose",
        "-f",
        str(COMPOSE_FILE),
        "exec",
        "-T",
        "api",
        "python",
        "-c",
        (
            "import sqlite3, json;"
            " conn = sqlite3.connect('development.db');"
            " rows = conn.execute('SELECT name FROM companies');"
            " print(json.dumps([r[0] for r in rows]))"
        ),
    ]
    out = subprocess.check_output(cmd, cwd=ROOT, env=env)
    names = json.loads(out.decode().strip())
    assert "https://example.com" in names
