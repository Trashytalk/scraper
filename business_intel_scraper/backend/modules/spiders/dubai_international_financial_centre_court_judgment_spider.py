"""Placeholder spider for Dubai International Financial Centre Court Judgment."""

import scrapy


class DubaiInternationalFinancialCentreCourtJudgmentSpider(scrapy.Spider):
    name = "dubai_international_financial_centre_court_judgment"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
