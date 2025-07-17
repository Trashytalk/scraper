from __future__ import annotations

from business_intel_scraper.backend.crawlers.spider import ExampleSpider


def test_example_spider_browser_mode(monkeypatch) -> None:
    class DummyCrawler:
        def __init__(self, headless=True) -> None:
            self.headless = headless

        def fetch(self, url: str) -> str:
            assert self.headless is False
            assert url == "https://example.com"
            return "<html></html>"

    monkeypatch.setattr(
        "business_intel_scraper.backend.crawlers.spider.BrowserCrawler",
        DummyCrawler,
    )
    spider = ExampleSpider(use_browser=True, headless=False)
    items = list(spider.start_requests())
    assert items == [{"url": "https://example.com"}]
