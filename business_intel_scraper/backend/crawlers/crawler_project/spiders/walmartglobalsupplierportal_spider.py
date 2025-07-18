"""Spider for Walmart Global Supplier Portal (placeholder)."""

import scrapy


class WalmartGlobalSupplierPortalSpider(scrapy.Spider):
    """Placeholder spider for Walmart Global Supplier Portal."""

    name = "walmartglobalsupplierportal"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
