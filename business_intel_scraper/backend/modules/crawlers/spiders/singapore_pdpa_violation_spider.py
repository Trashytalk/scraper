from __future__ import annotations

import scrapy


class SingaporePDPAViolationSpider(scrapy.Spider):
    """Singapore PDPA data breach violations."""

    name = "singapore_pdpa_violation"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
