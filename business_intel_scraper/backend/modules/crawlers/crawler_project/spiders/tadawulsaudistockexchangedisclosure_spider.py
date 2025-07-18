"""Spider for Tadawul Saudi Stock Exchange Disclosure (placeholder)."""

import scrapy


class TadawulSaudiStockExchangeDisclosureSpider(scrapy.Spider):
    """Placeholder spider for Tadawul Saudi Stock Exchange Disclosure."""

    name = "tadawulsaudistockexchangedisclosure"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
