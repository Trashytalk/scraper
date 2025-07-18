from __future__ import annotations

import scrapy


class SlovakiaNIAGrantSpider(scrapy.Spider):
    """Slovakia National Innovation Agency grants."""

    name = "slovakia_nia_grant"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
