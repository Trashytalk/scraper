"""Spider for Russia EGRUL (placeholder)."""

import scrapy


class RussiaEgrulSpider(scrapy.Spider):
    """Placeholder spider for Russia EGRUL."""

    name = "russiaegrul"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
