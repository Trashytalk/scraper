"""Spider for Singapore NEA Environmental Offender (placeholder)."""

import scrapy


class SingaporeNeaEnvironmentalOffenderSpider(scrapy.Spider):
    """Placeholder spider for Singapore NEA Environmental Offender."""

    name = "singaporeneaenvironmentaloffender"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
