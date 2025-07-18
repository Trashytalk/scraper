"""Placeholder spider for BCA Licensed Builders and Developers."""

import scrapy


class BcaLicensedBuildersDevelopersSpider(scrapy.Spider):
    name = "bca_licensed_builders_developers"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
