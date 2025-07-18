"""Spider for Kenya BRS Registry (placeholder)."""

import scrapy


class KenyaBrsRegistrySpider(scrapy.Spider):
    """Placeholder spider for Kenya BRS Registry."""

    name = "kenyabrsregistry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
