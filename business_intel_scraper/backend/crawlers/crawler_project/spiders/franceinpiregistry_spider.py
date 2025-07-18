"""Spider for France INPI Registry (placeholder)."""

import scrapy


class FranceInpiRegistrySpider(scrapy.Spider):
    """Placeholder spider for France INPI Registry."""

    name = "franceinpiregistry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
