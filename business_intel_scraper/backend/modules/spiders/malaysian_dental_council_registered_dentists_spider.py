"""Placeholder spider for Malaysian Dental Council Registered Dentists."""

import scrapy


class MalaysianDentalCouncilRegisteredDentistsSpider(scrapy.Spider):
    name = "malaysian_dental_council_registered_dentists"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
