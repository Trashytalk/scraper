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


def test_sherlock_scan_calls_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    called = {}

    def fake_run(username: str) -> dict[str, str]:
        called["username"] = username
        return {"username": username, "output": "ok"}

    monkeypatch.setattr(tasks, "run_sherlock", fake_run)
    result = tasks.sherlock_scan("alice")
    assert called["username"] == "alice"
    assert result == {"username": "alice", "output": "ok"}


def test_subfinder_scan_calls_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    called = {}

    def fake_run(domain: str) -> dict[str, str]:
        called["domain"] = domain
        return {"domain": domain, "output": "ok"}

    monkeypatch.setattr(tasks, "run_subfinder", fake_run)
    result = tasks.subfinder_scan("example.com")
    assert called["domain"] == "example.com"
    assert result == {"domain": "example.com", "output": "ok"}


def test_shodan_scan_calls_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    called = {}

    def fake_run(target: str) -> dict[str, str]:
        called["target"] = target
        return {"target": target, "output": "ok"}

    monkeypatch.setattr(tasks, "run_shodan", fake_run)
    result = tasks.shodan_scan("1.1.1.1")
    assert called["target"] == "1.1.1.1"
    assert result == {"target": "1.1.1.1", "output": "ok"}


def test_nmap_scan_calls_wrapper(monkeypatch: pytest.MonkeyPatch) -> None:
    called = {}

    def fake_run(target: str) -> dict[str, str]:
        called["target"] = target
        return {"target": target, "output": "ok"}

    monkeypatch.setattr(tasks, "run_nmap", fake_run)
    result = tasks.nmap_scan("example.com")
    assert called["target"] == "example.com"
    assert result == {"target": "example.com", "output": "ok"}


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
    monkeypatch.setattr(tasks.sherlock_scan, "apply_async", fake_apply_async)
    monkeypatch.setattr(tasks.subfinder_scan, "apply_async", fake_apply_async)
    monkeypatch.setattr(tasks.shodan_scan, "apply_async", fake_apply_async)
    monkeypatch.setattr(tasks.nmap_scan, "apply_async", fake_apply_async)

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

    recorded.clear()
    task_id = tasks.queue_sherlock_scan("alice")
    assert task_id == "abc123"
    assert recorded["args"] == ["alice"]

    recorded.clear()
    task_id = tasks.queue_subfinder_scan("example.net", countdown=5)
    assert task_id == "abc123"
    assert recorded["args"] == ["example.net"]
    assert recorded["countdown"] == 5

    recorded.clear()
    task_id = tasks.queue_shodan_scan("1.2.3.4")
    assert task_id == "abc123"
    assert recorded["args"] == ["1.2.3.4"]

    recorded.clear()
    task_id = tasks.queue_nmap_scan("example.org", queue="net")
    assert task_id == "abc123"
    assert recorded["args"] == ["example.org"]
    assert recorded["queue"] == "net"
