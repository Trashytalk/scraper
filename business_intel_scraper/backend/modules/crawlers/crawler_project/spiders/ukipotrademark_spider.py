"""Spider for UK IPO Trademark (placeholder)."""

import scrapy


class UkIpoTrademarkSpider(scrapy.Spider):
    """Placeholder spider for UK IPO Trademark."""

    name = "ukipotrademark"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
