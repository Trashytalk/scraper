"""Spider for Hong Kong CR Registry (placeholder)."""

import scrapy


class HongKongCrRegistrySpider(scrapy.Spider):
    """Placeholder spider for Hong Kong CR Registry."""

    name = "hongkongcrregistry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
