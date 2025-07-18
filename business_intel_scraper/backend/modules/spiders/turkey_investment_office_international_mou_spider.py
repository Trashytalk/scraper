"""Placeholder spider for Turkey Investment Office International MoU."""

import scrapy


class TurkeyInvestmentOfficeInternationalMouSpider(scrapy.Spider):
    name = "turkey_investment_office_international_mou"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
