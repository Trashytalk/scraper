from __future__ import annotations

import scrapy


class CommercialPropertyTaxArrearsSpider(scrapy.Spider):
    """Commercial property tax arrears."""

    name = "commercial_property_tax_arrears"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
