"""Spider for EPO Espacenet (placeholder)."""

import scrapy


class EpoEspacenetSpider(scrapy.Spider):
    """Placeholder spider for EPO Espacenet."""

    name = "epoespacenet"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
