"""Spider for Egypt Federation of Chambers of Commerce (placeholder)."""

import scrapy


class EgyptFederationOfChambersOfCommerceSpider(scrapy.Spider):
    """Placeholder spider for Egypt Federation of Chambers of Commerce."""

    name = "egyptfederationofchambersofcommerce"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
