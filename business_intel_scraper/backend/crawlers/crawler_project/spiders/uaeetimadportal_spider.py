"""Spider for UAE Etimad Portal (placeholder)."""

import scrapy


class UaeEtimadPortalSpider(scrapy.Spider):
    """Placeholder spider for UAE Etimad Portal."""

    name = "uaeetimadportal"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
