from __future__ import annotations

import scrapy


class LocalBusinessFastestGrowingSpider(scrapy.Spider):
    """Local business press fastest growing lists."""

    name = "local_business_fastest_growing"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
