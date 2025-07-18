from __future__ import annotations

import scrapy


class IndonesiaMOMBlacklistSpider(scrapy.Spider):
    """Indonesia Ministry of Manpower blacklist."""

    name = "indonesia_mom_blacklist"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
