from __future__ import annotations

import scrapy


class UkraineDefenseProcurementRecipientSpider(scrapy.Spider):
    """Ukraine defense procurement recipients."""

    name = "ukraine_defense_procurement_recipient"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
