"""Spider for Hong Kong Port Cargo Manifest (placeholder)."""

import scrapy


class HongKongPortCargoManifestSpider(scrapy.Spider):
    """Placeholder spider for Hong Kong Port Cargo Manifest."""

    name = "hongkongportcargomanifest"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
