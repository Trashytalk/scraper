from __future__ import annotations

import scrapy


class OmanTourismLicenseeSpider(scrapy.Spider):
    """Oman Ministry of Tourism licensees."""

    name = "oman_tourism_licensee"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
