"""Spider for UK Insolvency Service Notices (placeholder)."""

import scrapy


class UkInsolvencyServiceNoticesSpider(scrapy.Spider):
    """Placeholder spider for UK Insolvency Service Notices."""

    name = "ukinsolvencyservicenotices"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
