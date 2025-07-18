"""Spider for MAS Enforcement Singapore (placeholder)."""

import scrapy


class MasEnforcementSingaporeSpider(scrapy.Spider):
    """Placeholder spider for MAS Enforcement Singapore."""

    name = "masenforcementsingapore"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
