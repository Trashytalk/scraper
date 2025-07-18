"""Spider for GCC Patent Office (placeholder)."""

import scrapy


class GccPatentOfficeSpider(scrapy.Spider):
    """Placeholder spider for GCC Patent Office."""

    name = "gccpatentoffice"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
