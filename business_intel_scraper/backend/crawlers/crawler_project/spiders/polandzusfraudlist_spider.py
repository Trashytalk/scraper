"""Spider for Poland ZUS Fraud List (placeholder)."""

import scrapy


class PolandZusFraudListSpider(scrapy.Spider):
    """Placeholder spider for Poland ZUS Fraud List."""

    name = "polandzusfraudlist"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
