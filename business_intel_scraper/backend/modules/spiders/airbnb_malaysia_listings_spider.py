"""Placeholder spider for Airbnb Malaysia Listings."""

import scrapy


class AirbnbMalaysiaListingsSpider(scrapy.Spider):
    name = "airbnb_malaysia_listings"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
