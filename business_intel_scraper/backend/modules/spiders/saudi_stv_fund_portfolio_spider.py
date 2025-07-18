"""Placeholder spider for Saudi STV Fund Portfolio."""

import scrapy


class SaudiStvFundPortfolioSpider(scrapy.Spider):
    name = "saudi_stv_fund_portfolio"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
