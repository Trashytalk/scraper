"""Spider for FCA Warning Action UK (placeholder)."""

import scrapy


class FcaWarningActionUkSpider(scrapy.Spider):
    """Placeholder spider for FCA Warning Action UK."""

    name = "fcawarningactionuk"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
