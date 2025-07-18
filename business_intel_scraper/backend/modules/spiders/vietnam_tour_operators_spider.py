"""Placeholder spider for Vietnam National Administration of Tourism Tour Operators."""

import scrapy


class VietnamTourOperatorsSpider(scrapy.Spider):
    name = "vietnam_tour_operators"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
