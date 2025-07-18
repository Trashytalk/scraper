"""Foreign Exchange Control/Compliance Spider implementation."""

import scrapy


class ForeignExchangeControlComplianceSpider(scrapy.Spider):
    """Spider for Foreign Exchange Control/Compliance."""

    name = "foreign_exchange_control_compliance_spider"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        pass
