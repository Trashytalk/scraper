"""Spider for Brazil ANM Mining License Registry (placeholder)."""

import scrapy


class BrazilAnmMiningLicenseRegistrySpider(scrapy.Spider):
    """Placeholder spider for Brazil ANM Mining License Registry."""

    name = "brazilanmmininglicenseregistry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
