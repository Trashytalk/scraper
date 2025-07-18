"""Spider for US SEC Enforcement Action (placeholder)."""

import scrapy


class UsSecEnforcementActionSpider(scrapy.Spider):
    """Placeholder spider for US SEC Enforcement Action."""

    name = "ussecenforcementaction"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
