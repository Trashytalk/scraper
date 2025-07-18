"""Spider for Singapore ACRA Registry (placeholder)."""

import scrapy


class SingaporeAcraRegistrySpider(scrapy.Spider):
    """Placeholder spider for Singapore ACRA Registry."""

    name = "singaporeacraregistry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
