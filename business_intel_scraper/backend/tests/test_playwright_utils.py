from __future__ import annotations


import pytest

from business_intel_scraper.backend.modules.crawlers.playwright_utils import (
    fetch_with_playwright,
)
from business_intel_scraper.backend.proxy.manager import ProxyManager
from business_intel_scraper.backend.proxy.provider import DummyProxyProvider


@pytest.mark.asyncio
async def test_fetch_with_playwright_uses_proxy(monkeypatch) -> None:
    captured = {}

    def dummy_async_playwright():
        class DummyPlaywrightCM:
            async def __aenter__(self):
                class Chromium:
                    async def launch(self, headless=True, proxy=None):
                        captured["proxy"] = proxy

                        class Browser:
                            async def new_page(self):
                                class Page:
                                    async def goto(self, url):
                                        captured["url"] = url

                                    async def content(self):
                                        return "<html></html>"

                                return Page()

                            async def close(self):
                                pass

                        return Browser()

                class DummyPW:
                    chromium = Chromium()

                return DummyPW()

            async def __aexit__(self, exc_type, exc, tb):
                pass

        return DummyPlaywrightCM()

    monkeypatch.setattr(
        "business_intel_scraper.backend.modules.crawlers.playwright_utils.async_playwright",
        dummy_async_playwright,
    )
    provider = DummyProxyProvider(["http://proxy"])
    pm = ProxyManager(provider)
    html = await fetch_with_playwright("http://example.com", pm, headless=False)
    assert html == "<html></html>"
    assert captured["proxy"] == {"server": "http://proxy"}
    assert captured["url"] == "http://example.com"
