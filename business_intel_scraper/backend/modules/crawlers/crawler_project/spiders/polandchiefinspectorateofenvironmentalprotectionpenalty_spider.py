"""Spider for Poland Chief Inspectorate of Environmental Protection Penalty.

This is a placeholder implementation.
"""

import scrapy


class PolandChiefInspectorateOfEnvironmentalProtectionPenaltySpider(scrapy.Spider):
    """Placeholder spider for the environmental protection penalty registry."""

    name = "polandchiefinspectorateofenvironmentalprotectionpenalty"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
