"""Placeholder spider for Dubai Chamber Arbitration Award."""

import scrapy


class DubaiChamberArbitrationAwardSpider(scrapy.Spider):
    name = "dubai_chamber_arbitration_award"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
