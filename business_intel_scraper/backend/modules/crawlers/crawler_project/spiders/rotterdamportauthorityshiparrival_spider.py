"""Spider for Rotterdam Port Authority Ship Arrival (placeholder)."""

import scrapy


class RotterdamPortAuthorityShipArrivalSpider(scrapy.Spider):
    """Placeholder spider for Rotterdam Port Authority Ship Arrival."""

    name = "rotterdamportauthorityshiparrival"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
