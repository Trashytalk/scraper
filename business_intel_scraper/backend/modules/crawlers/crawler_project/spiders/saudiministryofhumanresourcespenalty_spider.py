"""Spider for Saudi Ministry of Human Resources Penalty (placeholder)."""

import scrapy


class SaudiMinistryOfHumanResourcesPenaltySpider(scrapy.Spider):
    """Placeholder spider for Saudi Ministry of Human Resources Penalty."""

    name = "saudiministryofhumanresourcespenalty"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
