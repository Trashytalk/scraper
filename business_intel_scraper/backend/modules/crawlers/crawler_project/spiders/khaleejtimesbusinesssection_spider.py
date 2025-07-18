"""Spider for Khaleej Times Business Section (placeholder)."""

import scrapy


class KhaleejTimesBusinessSectionSpider(scrapy.Spider):
    """Placeholder spider for Khaleej Times Business Section."""

    name = "khaleejtimesbusinesssection"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
