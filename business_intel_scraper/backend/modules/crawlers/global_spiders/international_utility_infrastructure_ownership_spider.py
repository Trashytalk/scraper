"""International Utility/Infrastructure Ownership Spider implementation."""

import scrapy


class InternationalUtilityInfrastructureOwnershipSpider(scrapy.Spider):
    """Spider for International Utility/Infrastructure Ownership."""

    name = "international_utility_infrastructure_ownership_spider"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        pass
