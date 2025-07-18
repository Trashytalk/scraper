"""Placeholder spider for Poland NCBR Grant List."""

import scrapy


class PolandNcbrGrantListSpider(scrapy.Spider):
    name = "poland_ncbr_grant_list"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
