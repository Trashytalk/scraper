from __future__ import annotations

import os
import sys
import pytest

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
)

# Import the tasks module
tasks = pytest.importorskip("business_intel_scraper.backend.workers.tasks")


def test_spiderfoot_scan_calls_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    called = {}

    def fake_run(domain: str) -> dict[str, str]:
        called["domain"] = domain
        return {"domain": domain, "output": "ok"}

    monkeypatch.setattr(tasks, "run_spiderfoot", fake_run)
    result = tasks.spiderfoot_scan("example.com")
    assert called["domain"] == "example.com"
    assert result == {"domain": "example.com", "output": "ok"}


def test_theharvester_scan_calls_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    called = {}

    def fake_run(domain: str) -> dict[str, str]:
        called["domain"] = domain
        return {"domain": domain, "output": "ok"}

    monkeypatch.setattr(tasks, "run_theharvester", fake_run)
    result = tasks.theharvester_scan("example.com")
    assert called["domain"] == "example.com"
    assert result == {"domain": "example.com", "output": "ok"}


def test_queue_functions(monkeypatch: pytest.MonkeyPatch) -> None:
    recorded = {}

    class DummyResult:
        def __init__(self, id: str) -> None:
            self.id = id

    def fake_apply_async(args=None, **kwargs):
        recorded["args"] = args
        recorded.update(kwargs)
        return DummyResult("abc123")

    monkeypatch.setattr(tasks.spiderfoot_scan, "apply_async", fake_apply_async)
    monkeypatch.setattr(tasks.theharvester_scan, "apply_async", fake_apply_async)

    task_id = tasks.queue_spiderfoot_scan("example.com", queue="osint", countdown=1)
    assert task_id == "abc123"
    assert recorded["args"] == ["example.com"]
    assert recorded["queue"] == "osint"
    assert recorded["countdown"] == 1

    recorded.clear()
    task_id = tasks.queue_theharvester_scan("example.org")
    assert task_id == "abc123"
    assert recorded["args"] == ["example.org"]
    assert "queue" not in recorded
    assert "countdown" not in recorded
