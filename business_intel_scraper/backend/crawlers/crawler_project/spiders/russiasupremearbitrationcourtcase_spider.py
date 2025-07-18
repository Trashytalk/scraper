"""Spider for Russia Supreme Arbitration Court Case (placeholder)."""

import scrapy


class RussiaSupremeArbitrationCourtCaseSpider(scrapy.Spider):
    """Placeholder spider for Russia Supreme Arbitration Court Case."""

    name = "russiasupremearbitrationcourtcase"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
