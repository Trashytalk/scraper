from __future__ import annotations

import scrapy


class LebanonBeirutBarCounselSpider(scrapy.Spider):
    """Lebanon Beirut Bar Association company counsel registry."""

    name = "lebanon_beirut_bar_counsel"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
