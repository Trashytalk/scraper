"""Spider for Jumia Major Seller (placeholder)."""

import scrapy


class JumiaMajorSellerSpider(scrapy.Spider):
    """Placeholder spider for Jumia Major Seller."""

    name = "jumiamajorseller"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
