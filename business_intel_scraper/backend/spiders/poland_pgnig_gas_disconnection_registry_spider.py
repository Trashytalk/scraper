"""Placeholder spider for Poland PGNiG Gas Disconnection Registry."""

import scrapy


class PolandPgnigGasDisconnectionRegistrySpider(scrapy.Spider):
    name = "poland_pgnig_gas_disconnection_registry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
