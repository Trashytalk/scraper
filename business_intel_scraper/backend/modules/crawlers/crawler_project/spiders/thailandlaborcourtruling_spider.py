"""Spider for Thailand Labor Court Ruling (placeholder)."""

import scrapy


class ThailandLaborCourtRulingSpider(scrapy.Spider):
    """Placeholder spider for Thailand Labor Court Ruling."""

    name = "thailandlaborcourtruling"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
