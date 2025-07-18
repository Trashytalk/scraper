"""Spider for London Stock Exchange RNS Filings (placeholder)."""

import scrapy


class LondonStockExchangeRnsFilingsSpider(scrapy.Spider):
    """Placeholder spider for London Stock Exchange RNS Filings."""

    name = "londonstockexchangernsfilings"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
