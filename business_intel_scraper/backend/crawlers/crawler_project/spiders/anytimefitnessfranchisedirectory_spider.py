"""Spider for Anytime Fitness Franchise Directory (placeholder)."""

import scrapy


class AnytimeFitnessFranchiseDirectorySpider(scrapy.Spider):
    """Placeholder spider for Anytime Fitness Franchise Directory."""

    name = "anytimefitnessfranchisedirectory"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
