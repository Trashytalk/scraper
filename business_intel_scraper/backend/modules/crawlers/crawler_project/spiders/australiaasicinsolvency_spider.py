"""Spider for Australia ASIC Insolvency (placeholder)."""

import scrapy


class AustraliaAsicInsolvencySpider(scrapy.Spider):
    """Placeholder spider for Australia ASIC Insolvency."""

    name = "australiaasicinsolvency"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
