"""Spider for ASIC Enforceable Undertaking Australia (placeholder)."""

import scrapy


class AsicEnforceableUndertakingAustraliaSpider(scrapy.Spider):
    """Placeholder spider for ASIC Enforceable Undertaking Australia."""

    name = "asicenforceableundertakingaustralia"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
