"""Spider for US Secretary of State Corporate Filing (placeholder)."""

import scrapy


class UsSecretaryOfStateCorporateFilingSpider(scrapy.Spider):
    """Placeholder spider for US Secretary of State Corporate Filing."""

    name = "ussecretaryofstatecorporatefiling"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
