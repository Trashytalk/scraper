"""Spider for Israel Defense Forces Vendor (placeholder)."""

import scrapy


class IsraelDefenseForcesVendorSpider(scrapy.Spider):
    """Placeholder spider for Israel Defense Forces Vendor."""

    name = "israeldefenseforcesvendor"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
