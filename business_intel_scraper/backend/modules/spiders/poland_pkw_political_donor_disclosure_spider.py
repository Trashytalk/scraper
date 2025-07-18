"""Placeholder spider for Poland PKW Political Donor Disclosure."""

import scrapy


class PolandPkwPoliticalDonorDisclosureSpider(scrapy.Spider):
    name = "poland_pkw_political_donor_disclosure"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
