"""Spider for UAE RERA Broker Registry (placeholder)."""

import scrapy


class UaeReraBrokerRegistrySpider(scrapy.Spider):
    """Placeholder spider for UAE RERA Broker Registry."""

    name = "uaererabrokerregistry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
