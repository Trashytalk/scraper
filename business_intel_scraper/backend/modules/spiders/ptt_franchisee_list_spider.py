"""Placeholder spider for PTT Franchisee List."""

import scrapy


class PttFranchiseeListSpider(scrapy.Spider):
    name = "ptt_franchisee_list"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
