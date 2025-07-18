"""Spider for Cross Shareholding Public Company (placeholder)."""

import scrapy


class CrossShareholdingPublicCompanySpider(scrapy.Spider):
    """Placeholder spider for Cross Shareholding Public Company."""

    name = "crossshareholdingpubliccompany"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
