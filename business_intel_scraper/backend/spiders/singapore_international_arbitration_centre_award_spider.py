"""Placeholder spider for Singapore International Arbitration Centre Award."""

import scrapy


class SingaporeInternationalArbitrationCentreAwardSpider(scrapy.Spider):
    name = "singapore_international_arbitration_centre_award"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
