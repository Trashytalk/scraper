"""Spider for France CCI Regional Member (placeholder)."""

import scrapy


class FranceCciRegionalMemberSpider(scrapy.Spider):
    """Placeholder spider for France CCI Regional Member."""

    name = "francecciregionalmember"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
