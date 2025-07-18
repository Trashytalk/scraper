"""Spider for UAE DED Company (placeholder)."""

import scrapy


class UaeDedCompanySpider(scrapy.Spider):
    """Placeholder spider for UAE DED Company."""

    name = "uaededcompany"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
