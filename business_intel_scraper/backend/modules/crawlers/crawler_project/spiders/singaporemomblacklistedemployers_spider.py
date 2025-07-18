"""Spider for Singapore MOM Blacklisted Employers (placeholder)."""

import scrapy


class SingaporeMomBlacklistedEmployersSpider(scrapy.Spider):
    """Placeholder spider for Singapore MOM Blacklisted Employers."""

    name = "singaporemomblacklistedemployers"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
