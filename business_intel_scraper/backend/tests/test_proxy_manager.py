"""Tests for ProxyManager utility."""

from __future__ import annotations

from business_intel_scraper.backend.utils import ProxyManager


def test_proxy_rotation() -> None:
    """Ensure proxies rotate correctly."""
    manager = ProxyManager(["proxy1", "proxy2"], rotate=True)
    assert manager.get_proxy() == "proxy1"
    assert manager.get_proxy() == "proxy2"
    assert manager.get_proxy() == "proxy1"


def test_random_selection() -> None:
    """Ensure random selection returns a proxy from the pool."""
    manager = ProxyManager(["proxy1", "proxy2"], rotate=False)
    assert manager.get_proxy() in {"proxy1", "proxy2"}


def test_add_remove_proxy() -> None:
    """Proxies can be added and removed from the pool."""
    manager = ProxyManager([])
    manager.add_proxy("proxy1")
    assert len(manager) == 1
    manager.remove_proxy("proxy1")
    assert len(manager) == 0
