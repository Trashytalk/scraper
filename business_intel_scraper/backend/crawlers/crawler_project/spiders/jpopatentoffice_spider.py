"""Spider for JPO Patent Office (placeholder)."""

import scrapy


class JpoPatentOfficeSpider(scrapy.Spider):
    """Placeholder spider for JPO Patent Office."""

    name = "jpopatentoffice"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
