"""Spider for Anadolu Agency Business (placeholder)."""

import scrapy


class AnadoluAgencyBusinessSpider(scrapy.Spider):
    """Placeholder spider for Anadolu Agency Business."""

    name = "anadoluagencybusiness"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
