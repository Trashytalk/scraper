"""Spider for SFC Enforcement News Hong Kong (placeholder)."""

import scrapy


class SfcEnforcementNewsHongKongSpider(scrapy.Spider):
    """Placeholder spider for SFC Enforcement News Hong Kong."""

    name = "sfcenforcementnewshongkong"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
