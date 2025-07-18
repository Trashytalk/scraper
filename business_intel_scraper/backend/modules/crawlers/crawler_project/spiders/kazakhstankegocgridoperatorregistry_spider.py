"""Spider for Kazakhstan KEGOC Grid Operator Registry (placeholder)."""

import scrapy


class KazakhstanKegocGridOperatorRegistrySpider(scrapy.Spider):
    """Placeholder spider for Kazakhstan KEGOC Grid Operator Registry."""

    name = "kazakhstankegocgridoperatorregistry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
