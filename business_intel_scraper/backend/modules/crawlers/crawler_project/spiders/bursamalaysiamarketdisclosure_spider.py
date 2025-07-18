"""Spider for Bursa Malaysia Market Disclosure (placeholder)."""

import scrapy


class BursaMalaysiaMarketDisclosureSpider(scrapy.Spider):
    """Placeholder spider for Bursa Malaysia Market Disclosure."""

    name = "bursamalaysiamarketdisclosure"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
