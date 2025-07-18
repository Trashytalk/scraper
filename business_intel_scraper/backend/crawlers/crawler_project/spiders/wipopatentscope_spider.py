"""Spider for WIPO PatentScope (placeholder)."""

import scrapy


class WipoPatentscopeSpider(scrapy.Spider):
    """Placeholder spider for WIPO PatentScope."""

    name = "wipopatentscope"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
