"""Placeholder spider for Sequoia India Portfolio Company."""

import scrapy


class SequoiaIndiaPortfolioCompanySpider(scrapy.Spider):
    name = "sequoia_india_portfolio_company"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
