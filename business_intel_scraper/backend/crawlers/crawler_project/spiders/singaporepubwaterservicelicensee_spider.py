"""Spider for Singapore PUB Water Service Licensee (placeholder)."""

import scrapy


class SingaporePubWaterServiceLicenseeSpider(scrapy.Spider):
    """Placeholder spider for Singapore PUB Water Service Licensee."""

    name = "singaporepubwaterservicelicensee"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
