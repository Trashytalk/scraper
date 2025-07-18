"""Placeholder spider for Selangor State Investment Centre Logistics Directory."""

import scrapy


class SelangorLogisticsDirectorySpider(scrapy.Spider):
    name = "selangor_logistics_directory"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
