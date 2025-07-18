"""Spider for Russia Federal Tax Service Delinquency Registry (placeholder)."""

import scrapy


class RussiaFederalTaxServiceDelinquencyRegistrySpider(scrapy.Spider):
    """Placeholder spider for Russia Federal Tax Service Delinquency Registry."""

    name = "russiafederaltaxservicedelinquencyregistry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
