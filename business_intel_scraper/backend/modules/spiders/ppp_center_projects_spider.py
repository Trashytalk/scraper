"""Placeholder spider for PPP Center Projects."""

import scrapy


class PppCenterProjectsSpider(scrapy.Spider):
    name = "ppp_center_projects"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
