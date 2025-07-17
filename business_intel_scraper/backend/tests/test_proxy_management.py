from __future__ import annotations

from business_intel_scraper.backend.proxy.manager import ProxyManager
from business_intel_scraper.backend.proxy.provider import DummyProxyProvider, APIProxyProvider


def test_dummy_provider_cycle() -> None:
    provider = DummyProxyProvider(["p1", "p2"])
    manager = ProxyManager(provider)
    assert manager.get_proxy() == "p1"
    assert manager.rotate_proxy() == "p2"
    assert manager.get_proxy() == "p2"


def test_api_proxy_provider(monkeypatch) -> None:
    calls: list[str] = []

    class Response:
        def __init__(self, text: str) -> None:
            self.text = text

        def raise_for_status(self) -> None:
            pass

    proxies = iter(["proxy1", "proxy2"])

    def fake_get(url: str, headers: dict[str, str] | None = None, timeout: int = 10) -> Response:
        calls.append(url)
        return Response(next(proxies))

    monkeypatch.setattr("business_intel_scraper.backend.proxy.provider.requests.get", fake_get)

    provider = APIProxyProvider("http://api.test", api_key="token")
    first = provider.get_proxy()
    second = provider.rotate()

    assert first == "proxy1"
    assert second == "proxy2"
    assert calls == ["http://api.test", "http://api.test"]
