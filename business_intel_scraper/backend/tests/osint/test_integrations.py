# ruff: noqa: E402
from types import SimpleNamespace
import shutil
import subprocess
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


from business_intel_scraper.backend.osint.integrations import (
    run_spiderfoot,
    run_theharvester,
    run_sherlock,
    run_subfinder,
)


def test_run_spiderfoot_missing(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: None)
    result = run_spiderfoot("example.com")
    assert result == {
        "domain": "example.com",
        "error": "SpiderFoot executable not found",
    }


def test_run_spiderfoot_success(monkeypatch):
    def fake_which(name):
        return "/usr/bin/spiderfoot" if name == "spiderfoot" else None

    monkeypatch.setattr(shutil, "which", fake_which)

    def fake_run(cmd, capture_output, text):
        assert cmd == ["/usr/bin/spiderfoot", "-q", "example.com", "-F", "json"]
        return SimpleNamespace(stdout="sf ok", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = run_spiderfoot("example.com")
    assert result == {"domain": "example.com", "output": "sf ok"}


def test_run_theharvester_missing(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: None)
    result = run_theharvester("example.com")
    assert result == {
        "domain": "example.com",
        "error": "theHarvester executable not found",
    }


def test_run_theharvester_success(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/theharvester")

    def fake_run(cmd, capture_output, text):
        assert cmd == ["/usr/bin/theharvester", "-d", "example.com", "-b", "all"]
        return SimpleNamespace(stdout="", stderr="th ok")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = run_theharvester("example.com")
    assert result == {"domain": "example.com", "output": "th ok"}


def test_run_sherlock_missing(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: None)
    result = run_sherlock("alice")
    assert result == {
        "username": "alice",
        "error": "sherlock executable not found",
    }


def test_run_sherlock_success(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/sherlock")

    def fake_run(cmd, capture_output, text):
        assert cmd == ["/usr/bin/sherlock", "alice", "--print-found"]
        return SimpleNamespace(stdout="found", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = run_sherlock("alice")
    assert result == {"username": "alice", "output": "found"}


def test_run_subfinder_missing(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: None)
    result = run_subfinder("example.com")
    assert result == {
        "domain": "example.com",
        "error": "subfinder executable not found",
    }


def test_run_subfinder_success(monkeypatch):
    monkeypatch.setattr(shutil, "which", lambda name: "/usr/bin/subfinder")

    def fake_run(cmd, capture_output, text):
        assert cmd == ["/usr/bin/subfinder", "-d", "example.com", "-silent"]
        return SimpleNamespace(stdout="sub1\nsub2", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = run_subfinder("example.com")
    assert result == {"domain": "example.com", "output": "sub1\nsub2"}
