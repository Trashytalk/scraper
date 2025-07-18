"""Spider for Egypt Tenders Portal (placeholder)."""

import scrapy


class EgyptTendersPortalSpider(scrapy.Spider):
    """Placeholder spider for Egypt Tenders Portal."""

    name = "egypttendersportal"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
