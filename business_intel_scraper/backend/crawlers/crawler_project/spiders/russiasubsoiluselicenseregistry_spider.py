"""Spider for Russia Subsoil Use License Registry (placeholder)."""

import scrapy


class RussiaSubsoilUseLicenseRegistrySpider(scrapy.Spider):
    """Placeholder spider for Russia Subsoil Use License Registry."""

    name = "russiasubsoiluselicenseregistry"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
