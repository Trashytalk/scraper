"""Spider for Poland KRS (placeholder)."""

import scrapy


class PolandKrsSpider(scrapy.Spider):
    """Placeholder spider for Poland KRS."""

    name = "polandkrs"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
