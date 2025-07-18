"""Placeholder spider for Singapore Charity Portal Business Link."""

import scrapy


class SingaporeCharityPortalBusinessLinkSpider(scrapy.Spider):
    name = "singapore_charity_portal_business_link"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
