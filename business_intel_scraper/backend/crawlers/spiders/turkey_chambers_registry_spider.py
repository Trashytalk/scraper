from __future__ import annotations

import scrapy


class TurkeyChambersRegistrySpider(scrapy.Spider):
    """Turkey Chambers of Agriculture/Industry registries."""

    name = "turkey_chambers_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
