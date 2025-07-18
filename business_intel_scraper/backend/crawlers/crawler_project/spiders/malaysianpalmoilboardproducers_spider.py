"""Spider for Malaysian Palm Oil Board Producers (placeholder)."""

import scrapy


class MalaysianPalmOilBoardProducersSpider(scrapy.Spider):
    """Placeholder spider for Malaysian Palm Oil Board Producers."""

    name = "malaysianpalmoilboardproducers"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
