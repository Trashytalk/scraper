"""Spider for UK Ministry of Justice Case Law (placeholder)."""

import scrapy


class UkMinistryOfJusticeCaseLawSpider(scrapy.Spider):
    """Placeholder spider for UK Ministry of Justice Case Law."""

    name = "ukministryofjusticecaselaw"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
