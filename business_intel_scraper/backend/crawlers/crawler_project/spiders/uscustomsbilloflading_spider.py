"""Spider for US Customs Bill of Lading (placeholder)."""

import scrapy


class UsCustomsBillOfLadingSpider(scrapy.Spider):
    """Placeholder spider for US Customs Bill of Lading."""

    name = "uscustomsbilloflading"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
