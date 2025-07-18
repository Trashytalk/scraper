"""Placeholder spider for Poland Enterprise Investors Portfolio."""

import scrapy


class PolandEnterpriseInvestorsPortfolioSpider(scrapy.Spider):
    name = "poland_enterprise_investors_portfolio"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
