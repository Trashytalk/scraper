"""Placeholder spider for Vietnam Association of Realtors."""

import scrapy


class VietnamAssociationOfRealtorsSpider(scrapy.Spider):
    name = "vietnam_association_of_realtors"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
