"""Placeholder spider for Singapore Pasar Directory."""

import scrapy


class SingaporePasarDirectorySpider(scrapy.Spider):
    name = "singapore_pasar_directory"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
