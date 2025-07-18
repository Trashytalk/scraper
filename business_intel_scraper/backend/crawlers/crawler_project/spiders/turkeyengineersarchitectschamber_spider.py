"""Spider for Turkey Engineers Architects Chamber (placeholder)."""

import scrapy


class TurkeyEngineersArchitectsChamberSpider(scrapy.Spider):
    """Placeholder spider for Turkey Engineers Architects Chamber."""

    name = "turkeyengineersarchitectschamber"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
