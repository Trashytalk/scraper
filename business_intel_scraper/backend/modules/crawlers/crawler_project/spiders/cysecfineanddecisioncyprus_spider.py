"""Spider for CySEC Fine and Decision Cyprus (placeholder)."""

import scrapy


class CysecFineAndDecisionCyprusSpider(scrapy.Spider):
    """Placeholder spider for CySEC Fine and Decision Cyprus."""

    name = "cysecfineanddecisioncyprus"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
