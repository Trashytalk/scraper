"""Spider for India Railways Approved Vendor (placeholder)."""

import scrapy


class IndiaRailwaysApprovedVendorSpider(scrapy.Spider):
    """Placeholder spider for India Railways Approved Vendor."""

    name = "indiarailwaysapprovedvendor"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
