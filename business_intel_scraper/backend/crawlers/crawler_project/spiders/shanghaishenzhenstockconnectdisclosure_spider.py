"""Spider for Shanghai Shenzhen Stock Connect Disclosure (placeholder)."""

import scrapy


class ShanghaiShenzhenStockConnectDisclosureSpider(scrapy.Spider):
    """Placeholder spider for Shanghai Shenzhen Stock Connect Disclosure."""

    name = "shanghaishenzhenstockconnectdisclosure"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
