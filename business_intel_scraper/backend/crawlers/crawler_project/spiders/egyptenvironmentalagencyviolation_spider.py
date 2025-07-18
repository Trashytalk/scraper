"""Spider for Egypt Environmental Agency Violation (placeholder)."""

import scrapy


class EgyptEnvironmentalAgencyViolationSpider(scrapy.Spider):
    """Placeholder spider for Egypt Environmental Agency Violation."""

    name = "egyptenvironmentalagencyviolation"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
