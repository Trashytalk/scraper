"""Spider for Philippines PRC Licensee (placeholder)."""

import scrapy


class PhilippinesPrcLicenseeSpider(scrapy.Spider):
    """Placeholder spider for Philippines PRC Licensee."""

    name = "philippinesprclicensee"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
