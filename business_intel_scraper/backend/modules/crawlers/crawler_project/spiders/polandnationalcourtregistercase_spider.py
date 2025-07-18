"""Spider for Poland National Court Register Case (placeholder)."""

import scrapy


class PolandNationalCourtRegisterCaseSpider(scrapy.Spider):
    """Placeholder spider for Poland National Court Register Case."""

    name = "polandnationalcourtregistercase"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
