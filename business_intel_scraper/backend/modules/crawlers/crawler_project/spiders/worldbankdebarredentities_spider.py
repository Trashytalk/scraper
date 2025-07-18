"""Spider for World Bank Debarred Entities (placeholder)."""

import scrapy


class WorldBankDebarredEntitiesSpider(scrapy.Spider):
    """Placeholder spider for World Bank Debarred Entities."""

    name = "worldbankdebarredentities"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
