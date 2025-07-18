from __future__ import annotations

import scrapy


class PublicProcurementComplaintSpider(scrapy.Spider):
    """Public procurement complaint and appeal board."""

    name = "public_procurement_complaint"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
