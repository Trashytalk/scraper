"""Spider for UK Companies House (placeholder)."""

import scrapy


class UkCompaniesHouseSpider(scrapy.Spider):
    """Placeholder spider for UK Companies House."""

    name = "ukcompanieshouse"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
