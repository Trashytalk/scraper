"""Spider for Saudi Contractors Authority Accredited (placeholder)."""

import scrapy


class SaudiContractorsAuthorityAccreditedSpider(scrapy.Spider):
    """Placeholder spider for Saudi Contractors Authority Accredited."""

    name = "saudicontractorsauthorityaccredited"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
