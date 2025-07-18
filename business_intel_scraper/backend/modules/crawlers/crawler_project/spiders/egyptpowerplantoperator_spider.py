"""Spider for Egypt Power Plant Operator (placeholder)."""

import scrapy


class EgyptPowerPlantOperatorSpider(scrapy.Spider):
    """Placeholder spider for Egypt Power Plant Operator."""

    name = "egyptpowerplantoperator"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
