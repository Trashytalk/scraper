"""Spider for Turkey Ministry of Environment Fine (placeholder)."""

import scrapy


class TurkeyMinistryOfEnvironmentFineSpider(scrapy.Spider):
    """Placeholder spider for Turkey Ministry of Environment Fine."""

    name = "turkeyministryofenvironmentfine"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
