"""Spider for Tokyo Stock Exchange TSE Filings (placeholder)."""

import scrapy


class TokyoStockExchangeTseFilingsSpider(scrapy.Spider):
    """Placeholder spider for Tokyo Stock Exchange TSE Filings."""

    name = "tokyostockexchangetsefilings"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
