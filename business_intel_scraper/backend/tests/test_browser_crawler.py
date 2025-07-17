from __future__ import annotations

import pytest

from business_intel_scraper.backend.crawlers.browser import BrowserCrawler


def test_browser_crawler_requires_dependency(monkeypatch) -> None:
    """Ensure RuntimeError raised when no browser backends available."""
    monkeypatch.setattr(
        "business_intel_scraper.backend.crawlers.browser.sync_playwright", None
    )
    monkeypatch.setattr(
        "business_intel_scraper.backend.crawlers.browser.webdriver", None
    )
    monkeypatch.setattr(
        "business_intel_scraper.backend.crawlers.browser.ChromeOptions", None
    )
    crawler = BrowserCrawler()
    with pytest.raises(RuntimeError):
        crawler.fetch("https://example.com")

