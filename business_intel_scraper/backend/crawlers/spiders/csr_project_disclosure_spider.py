from __future__ import annotations

import scrapy


class CSRProjectDisclosureSpider(scrapy.Spider):
    """Corporate social responsibility project disclosures."""

    name = "csr_project_disclosure"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
