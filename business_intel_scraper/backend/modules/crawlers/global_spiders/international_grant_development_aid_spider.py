"""International Grant/Development Aid Spider implementation."""

import scrapy


class InternationalGrantDevelopmentAidSpider(scrapy.Spider):
    """Spider for International Grant/Development Aid."""

    name = "international_grant_development_aid_spider"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        pass
