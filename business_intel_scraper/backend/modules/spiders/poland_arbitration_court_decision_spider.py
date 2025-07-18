"""Placeholder spider for Poland Arbitration Court Decision."""

import scrapy


class PolandArbitrationCourtDecisionSpider(scrapy.Spider):
    name = "poland_arbitration_court_decision"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
