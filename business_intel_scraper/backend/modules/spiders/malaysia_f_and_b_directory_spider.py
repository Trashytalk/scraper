"""Placeholder spider for Malaysia F&B Directory."""

import scrapy


class MalaysiaFAndBDirectorySpider(scrapy.Spider):
    name = "malaysia_f_and_b_directory"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
