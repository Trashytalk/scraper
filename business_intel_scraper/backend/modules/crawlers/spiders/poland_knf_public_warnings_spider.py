from __future__ import annotations

import scrapy


class PolandKNFPublicWarningsSpider(scrapy.Spider):
    """Poland Financial Supervision Authority public warnings."""

    name = "poland_knf_public_warnings"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
