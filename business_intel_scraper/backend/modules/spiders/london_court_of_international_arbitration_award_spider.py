"""Placeholder spider for London Court of International Arbitration Award."""

import scrapy


class LondonCourtOfInternationalArbitrationAwardSpider(scrapy.Spider):
    name = "london_court_of_international_arbitration_award"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
