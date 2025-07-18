"""Non-US Sanctions List Spider implementation."""

import scrapy


class NonUsSanctionsListSpider(scrapy.Spider):
    """Spider for Non-US Sanctions List."""

    name = "non_us_sanctions_list_spider"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        pass
