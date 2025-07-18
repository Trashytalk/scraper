"""Spider for Singapore GeBIZ Registered Vendor (placeholder)."""

import scrapy


class SingaporeGebizRegisteredVendorSpider(scrapy.Spider):
    """Placeholder spider for Singapore GeBIZ Registered Vendor."""

    name = "singaporegebizregisteredvendor"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
