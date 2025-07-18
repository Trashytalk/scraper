"""Placeholder spider for Turkey Diyanet Foundation Business List."""

import scrapy


class TurkeyDiyanetFoundationBusinessListSpider(scrapy.Spider):
    name = "turkey_diyanet_foundation_business_list"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
