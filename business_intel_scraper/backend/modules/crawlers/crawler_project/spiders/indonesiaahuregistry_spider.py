"""Spider for Indonesia AHU Registry (placeholder)."""

import scrapy


class IndonesiaAhuRegistrySpider(scrapy.Spider):
    """Placeholder spider for Indonesia AHU Registry."""

    name = "indonesiaahuregistry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
