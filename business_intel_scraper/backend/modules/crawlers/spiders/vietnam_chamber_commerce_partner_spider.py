from __future__ import annotations

import scrapy


class VietnamChamberCommercePartnerSpider(scrapy.Spider):
    """Vietnam Chamber of Commerce international partners."""

    name = "vietnam_chamber_commerce_partner"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
