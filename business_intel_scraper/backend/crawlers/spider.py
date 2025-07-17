"""Example Scrapy spider."""

from __future__ import annotations

import scrapy

from ..security import solve_captcha

from ..proxy.provider import DummyProxyProvider
from .browser import BrowserCrawler


class ExampleSpider(scrapy.Spider):
    """Simple spider that scrapes example.com."""

    name = "example"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com"]

    # Configure proxy middleware and provider
    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            (
                "business_intel_scraper.backend.crawlers.middleware." "ProxyMiddleware"
            ): 543,
            (
                "business_intel_scraper.backend.crawlers.middleware."
                "RandomUserAgentMiddleware"
            ): 544,
            (
                "business_intel_scraper.backend.crawlers.middleware."
                "RandomDelayMiddleware"
            ): 545,
        },
        "PROXY_PROVIDER": DummyProxyProvider(["http://localhost:8000"]),
    }

    def __init__(
        self,
        *args,
        use_browser: bool = False,
        headless: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.use_browser = use_browser
        self.headless = headless

    def start_requests(self):
        if self.use_browser:
            crawler = BrowserCrawler(headless=self.headless)
            for url in self.start_urls:
                html = crawler.fetch(url)
                response = scrapy.http.TextResponse(url=url, body=html.encode("utf-8"))
                yield self.parse(response)
        else:
            for url in self.start_urls:
                yield scrapy.Request(url, callback=self.parse)

    def parse(
        self,
        response: scrapy.http.Response,
    ) -> scrapy.Item | dict[str, str]:
        """Parse the response.

        Parameters
        ----------
        response : scrapy.http.Response
            The HTTP response to parse.

        Returns
        -------
        scrapy.Item | dict[str, str]
            Parsed item from the page.
        """
        if "captcha" in response.text.lower():
            solve_captcha(b"dummy")
            return {}

        return {"url": response.url}
