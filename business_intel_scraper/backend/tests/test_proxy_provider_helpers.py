import os
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[3]))

from business_intel_scraper.backend.proxy.provider import (
    fetch_fresh_proxies,
    fetch_fresh_proxy,
)


def test_fetch_fresh_proxies(monkeypatch):
    calls = []

    class Response:
        def __init__(self, text):
            self.text = text

        def raise_for_status(self):
            pass

    def fake_get(url, headers=None, timeout=10):
        calls.append((url, headers))
        return Response("p1\np2\n")

    monkeypatch.setattr(
        "business_intel_scraper.backend.proxy.provider.requests.get", fake_get
    )

    proxies = fetch_fresh_proxies("http://service", api_key="token")

    assert proxies == ["p1", "p2"]
    assert calls == [("http://service", {"Authorization": "token"})]


def test_fetch_fresh_proxy_empty(monkeypatch):
    def fake_fetch(endpoint, api_key=None):
        return []

    monkeypatch.setattr(
        "business_intel_scraper.backend.proxy.provider.fetch_fresh_proxies",
        fake_fetch,
    )

    with pytest.raises(RuntimeError):
        fetch_fresh_proxy("http://service")


def test_fetch_fresh_proxy(monkeypatch):
    monkeypatch.setattr(
        "business_intel_scraper.backend.proxy.provider.fetch_fresh_proxies",
        lambda *_: ["px", "py"],
    )

    proxy = fetch_fresh_proxy("http://service")
    assert proxy == "px"
