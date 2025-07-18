"""Spider for India MCA Registry (placeholder)."""

import scrapy


class IndiaMcaRegistrySpider(scrapy.Spider):
    """Placeholder spider for India MCA Registry."""

    name = "indiamcaregistry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
