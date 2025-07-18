"""Placeholder spider for Bureau of Customs Accredited Brokers."""

import scrapy


class BureauOfCustomsAccreditedBrokersSpider(scrapy.Spider):
    name = "bureau_of_customs_accredited_brokers"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
