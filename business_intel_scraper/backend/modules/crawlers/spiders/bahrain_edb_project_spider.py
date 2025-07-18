from __future__ import annotations

import scrapy


class BahrainEDBProjectSpider(scrapy.Spider):
    """Bahrain Economic Development Board projects."""

    name = "bahrain_edb_project"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
