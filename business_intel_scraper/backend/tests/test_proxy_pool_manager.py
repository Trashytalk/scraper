from __future__ import annotations

"""Tests for ProxyPoolManager utility."""

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
