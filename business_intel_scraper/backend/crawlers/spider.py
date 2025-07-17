"""Example Scrapy spider."""

from __future__ import annotations

import scrapy

from .middleware import ProxyMiddleware
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
            "business_intel_scraper.backend.crawlers.middleware.RandomUserAgentMiddleware": 544,
            "business_intel_scraper.backend.crawlers.middleware.RandomDelayMiddleware": 545,
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
        return {"url": response.url}
