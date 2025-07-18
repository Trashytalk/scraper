"""Placeholder spider for Poland Local Municipality Property Lien."""

import scrapy


class PolandLocalMunicipalityPropertyLienSpider(scrapy.Spider):
    name = "poland_local_municipality_property_lien"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
