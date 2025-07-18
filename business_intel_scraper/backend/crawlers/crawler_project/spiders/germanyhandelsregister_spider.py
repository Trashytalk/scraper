"""Spider for Germany Handelsregister (placeholder)."""

import scrapy


class GermanyHandelsregisterSpider(scrapy.Spider):
    """Placeholder spider for Germany Handelsregister."""

    name = "germanyhandelsregister"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
