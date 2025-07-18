"""Spider for UAE ADNOC Vendor List (placeholder)."""

import scrapy


class UaeAdnocVendorListSpider(scrapy.Spider):
    """Placeholder spider for UAE ADNOC Vendor List."""

    name = "uaeadnocvendorlist"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
