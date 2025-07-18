"""Spider for UK HMT Financial Sanctions (placeholder)."""

import scrapy


class UkHmtFinancialSanctionsSpider(scrapy.Spider):
    """Placeholder spider for UK HMT Financial Sanctions."""

    name = "ukhmtfinancialsanctions"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
