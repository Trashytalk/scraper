"""Spider for UAE Ministry of Economy Importer Registry (placeholder)."""

import scrapy


class UaeMinistryOfEconomyImporterRegistrySpider(scrapy.Spider):
    """Placeholder spider for UAE Ministry of Economy Importer Registry."""

    name = "uaeministryofeconomyimporterregistry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
