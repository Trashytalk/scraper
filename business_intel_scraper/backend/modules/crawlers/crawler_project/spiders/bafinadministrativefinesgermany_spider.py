"""Spider for BaFin Administrative Fines Germany (placeholder)."""

import scrapy


class BafinAdministrativeFinesGermanySpider(scrapy.Spider):
    """Placeholder spider for BaFin Administrative Fines Germany."""

    name = "bafinadministrativefinesgermany"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
