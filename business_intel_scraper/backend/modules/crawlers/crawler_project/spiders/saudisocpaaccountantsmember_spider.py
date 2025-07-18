"""Spider for Saudi SOCPA Accountants Member (placeholder)."""

import scrapy


class SaudiSocpaAccountantsMemberSpider(scrapy.Spider):
    """Placeholder spider for Saudi SOCPA Accountants Member."""

    name = "saudisocpaaccountantsmember"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
