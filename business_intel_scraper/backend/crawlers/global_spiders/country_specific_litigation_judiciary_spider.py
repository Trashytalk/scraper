"""Country-Specific Litigation/Judiciary Spider implementation."""

import scrapy


class CountrySpecificLitigationJudiciarySpider(scrapy.Spider):
    """Spider for Country-Specific Litigation/Judiciary."""

    name = "country_specific_litigation_judiciary_spider"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        pass
