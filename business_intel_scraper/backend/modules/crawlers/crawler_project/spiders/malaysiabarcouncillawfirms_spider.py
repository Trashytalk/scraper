"""Spider for Malaysia Bar Council Law Firms (placeholder)."""

import scrapy


class MalaysiaBarCouncilLawFirmsSpider(scrapy.Spider):
    """Placeholder spider for Malaysia Bar Council Law Firms."""

    name = "malaysiabarcouncillawfirms"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
