"""Spider for Straits Times Singapore Business (placeholder)."""

import scrapy


class StraitsTimesSingaporeBusinessSpider(scrapy.Spider):
    """Placeholder spider for Straits Times Singapore Business."""

    name = "straitstimessingaporebusiness"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
