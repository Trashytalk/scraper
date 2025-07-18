"""Spider for India CPPP Tender Award (placeholder)."""

import scrapy


class IndiaCpppTenderAwardSpider(scrapy.Spider):
    """Placeholder spider for India CPPP Tender Award."""

    name = "indiacppptenderaward"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
