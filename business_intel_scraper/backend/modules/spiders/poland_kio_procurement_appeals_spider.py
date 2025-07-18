"""Placeholder spider for Poland KIO Procurement Appeals."""

import scrapy


class PolandKioProcurementAppealsSpider(scrapy.Spider):
    name = "poland_kio_procurement_appeals"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
