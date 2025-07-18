"""Placeholder spider for Singapore Temasek Holdings Investment."""

import scrapy


class SingaporeTemasekHoldingsInvestmentSpider(scrapy.Spider):
    name = "singapore_temasek_holdings_investment"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
