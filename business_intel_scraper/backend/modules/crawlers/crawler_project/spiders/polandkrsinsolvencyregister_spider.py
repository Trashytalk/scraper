"""Spider for Poland KRS Insolvency Register (placeholder)."""

import scrapy


class PolandKrsInsolvencyRegisterSpider(scrapy.Spider):
    """Placeholder spider for Poland KRS Insolvency Register."""

    name = "polandkrsinsolvencyregister"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
