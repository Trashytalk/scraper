"""Spider for Allegro Seller Profile (placeholder)."""

import scrapy


class AllegroSellerProfileSpider(scrapy.Spider):
    """Placeholder spider for Allegro Seller Profile."""

    name = "allegrosellerprofile"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
