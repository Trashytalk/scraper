"""Spider for UK Contracts Finder (placeholder)."""

import scrapy


class UkContractsFinderSpider(scrapy.Spider):
    """Placeholder spider for UK Contracts Finder."""

    name = "ukcontractsfinder"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
