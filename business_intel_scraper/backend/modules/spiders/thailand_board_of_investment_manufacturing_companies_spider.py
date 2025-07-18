"""Placeholder spider for Thailand Board of Investment - Manufacturing Companies."""

import scrapy


class ThailandBoardOfInvestmentManufacturingCompaniesSpider(scrapy.Spider):
    name = "thailand_board_of_investment_manufacturing_companies"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
