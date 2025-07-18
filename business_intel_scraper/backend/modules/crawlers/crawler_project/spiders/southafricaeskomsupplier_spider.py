"""Spider for South Africa Eskom Supplier (placeholder)."""

import scrapy


class SouthAfricaEskomSupplierSpider(scrapy.Spider):
    """Placeholder spider for South Africa Eskom Supplier."""

    name = "southafricaeskomsupplier"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
