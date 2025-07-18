"""Spider for Financial Times Company News (placeholder)."""

import scrapy


class FinancialTimesCompanyNewsSpider(scrapy.Spider):
    """Placeholder spider for Financial Times Company News."""

    name = "financialtimescompanynews"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
