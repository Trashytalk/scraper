"""Spider for EU TARIC Changes (placeholder)."""

import scrapy


class EuTaricChangesSpider(scrapy.Spider):
    """Placeholder spider for EU TARIC Changes."""

    name = "eutaricchanges"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
