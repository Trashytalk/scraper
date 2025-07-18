"""Spider for Malaysia ePerolehan (placeholder)."""

import scrapy


class MalaysiaEperolehanSpider(scrapy.Spider):
    """Placeholder spider for Malaysia ePerolehan."""

    name = "malaysiaeperolehan"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
