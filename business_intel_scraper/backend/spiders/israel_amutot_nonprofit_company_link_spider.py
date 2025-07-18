"""Placeholder spider for Israel Amutot Nonprofit-Company Link."""

import scrapy


class IsraelAmutotNonprofitCompanyLinkSpider(scrapy.Spider):
    name = "israel_amutot_nonprofit_company_link"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
