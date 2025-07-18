"""Placeholder spider for Poland KNF Public Warning List."""

import scrapy


class PolandKnfPublicWarningListSpider(scrapy.Spider):
    name = "poland_knf_public_warning_list"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
