"""Placeholder spider for Singapore Green Labelling Scheme Certified Companies."""

import scrapy


class SingaporeGreenLabellingSchemeCertifiedCompaniesSpider(scrapy.Spider):
    name = "singapore_green_labelling_scheme_certified_companies"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
