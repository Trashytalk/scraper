"""Placeholder spider for AgFunder SEA Startup Directory."""

import scrapy


class AgfunderSeaStartupDirectorySpider(scrapy.Spider):
    name = "agfunder_sea_startup_directory"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
