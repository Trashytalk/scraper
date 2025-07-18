"""Spider for Saudi Aramco Approved Vendor List (placeholder)."""

import scrapy


class SaudiAramcoApprovedVendorListSpider(scrapy.Spider):
    """Placeholder spider for Saudi Aramco Approved Vendor List."""

    name = "saudiaramcoapprovedvendorlist"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
