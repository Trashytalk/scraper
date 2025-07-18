"""Spider for Saudi Arabia CR Registry (placeholder)."""

import scrapy


class SaudiArabiaCrRegistrySpider(scrapy.Spider):
    """Placeholder spider for Saudi Arabia CR Registry."""

    name = "saudiarabiacrregistry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
