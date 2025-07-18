"""Spider for Malaysia DOE Environmental Violation (placeholder)."""

import scrapy


class MalaysiaDoeEnvironmentalViolationSpider(scrapy.Spider):
    """Placeholder spider for Malaysia DOE Environmental Violation."""

    name = "malaysiadoeenvironmentalviolation"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
