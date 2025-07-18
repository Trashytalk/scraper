from __future__ import annotations

import scrapy


class SerbiaMMELicenseeSpider(scrapy.Spider):
    """Serbia Ministry of Mining and Energy licensees."""

    name = "serbia_mme_licensee"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
