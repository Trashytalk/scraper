"""Spider for Swiss SECO Sanctions (placeholder)."""

import scrapy


class SwissSecoSanctionsSpider(scrapy.Spider):
    """Placeholder spider for Swiss SECO Sanctions."""

    name = "swisssecosanctions"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
