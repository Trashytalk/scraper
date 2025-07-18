"""Tests for ProxyPoolManager utility."""

from __future__ import annotations

from business_intel_scraper.backend.proxy.proxy_manager import ProxyPoolManager


def test_rotation_cycle(monkeypatch) -> None:
    manager = ProxyPoolManager(["p1", "p2"], rotate=True, validator=lambda p: True)
    assert manager.get_proxy() == "p1"
    assert manager.get_proxy() == "p2"
    assert manager.get_proxy() == "p1"


def test_invalid_proxy_removed() -> None:
    manager = ProxyPoolManager(
        [
            "bad",
            "good",
        ],
        rotate=True,
        validator=lambda p: p != "bad",
    )
    proxy = manager.get_proxy()
    assert proxy == "good"
    assert len(manager) == 1


def test_add_and_remove_proxy() -> None:
    manager = ProxyPoolManager([], rotate=False, validator=lambda p: True)
    manager.add_proxy("p1")
    manager.add_proxy("p2")
    assert len(manager) == 2
    manager.remove_proxy("p1")
    assert len(manager) == 1
    assert manager.get_proxy() == "p2"


def test_remove_missing_proxy() -> None:
    manager = ProxyPoolManager(["p1"], validator=lambda p: True)
    manager.remove_proxy("does-not-exist")
    assert len(manager) == 1


def test_get_proxy_empty() -> None:
    manager = ProxyPoolManager([])
    assert manager.get_proxy() is None


def test_default_validator_failure(monkeypatch) -> None:
    def fake_get(*_args, **_kwargs):
        raise RuntimeError("network")

    monkeypatch.setattr(
        "business_intel_scraper.backend.proxy.proxy_manager.requests.get", fake_get
    )

    manager = ProxyPoolManager(["p1"])
    assert manager.get_proxy() is None
    assert len(manager) == 0
