"""Spider for Malaysia LHDN Tax Arrears (placeholder)."""

import scrapy


class MalaysiaLhdnTaxArrearsSpider(scrapy.Spider):
    """Placeholder spider for Malaysia LHDN Tax Arrears."""

    name = "malaysialhdntaxarrears"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
