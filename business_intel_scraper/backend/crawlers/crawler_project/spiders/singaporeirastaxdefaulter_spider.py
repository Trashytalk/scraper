"""Spider for Singapore IRAS Tax Defaulter (placeholder)."""

import scrapy


class SingaporeIrasTaxDefaulterSpider(scrapy.Spider):
    """Placeholder spider for Singapore IRAS Tax Defaulter."""

    name = "singaporeirastaxdefaulter"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
