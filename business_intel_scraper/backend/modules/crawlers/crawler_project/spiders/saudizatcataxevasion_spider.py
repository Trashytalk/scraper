"""Spider for Saudi ZATCA Tax Evasion (placeholder)."""

import scrapy


class SaudiZatcaTaxEvasionSpider(scrapy.Spider):
    """Placeholder spider for Saudi ZATCA Tax Evasion."""

    name = "saudizatcataxevasion"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
