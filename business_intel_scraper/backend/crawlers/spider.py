"""Example Scrapy spider."""

from __future__ import annotations

import scrapy

from ..security import solve_captcha

from ..proxy.provider import DummyProxyProvider


class ExampleSpider(scrapy.Spider):
    """Simple spider that scrapes example.com."""

    name = "example"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com"]

    # Configure proxy middleware and provider
    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            "business_intel_scraper.backend.crawlers.middleware.ProxyMiddleware": 543,
        },
        "PROXY_PROVIDER": DummyProxyProvider(["http://localhost:8000"]),
    }

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
