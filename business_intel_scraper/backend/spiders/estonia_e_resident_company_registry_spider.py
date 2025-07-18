"""Placeholder spider for Estonia e-Resident Company Registry."""

import scrapy


class EstoniaEResidentCompanyRegistrySpider(scrapy.Spider):
    name = "estonia_e_resident_company_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
