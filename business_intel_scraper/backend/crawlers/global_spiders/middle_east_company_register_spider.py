"""Middle East Company Register Spider implementation."""

import scrapy


class MiddleEastCompanyRegisterSpider(scrapy.Spider):
    """Spider for Middle East Company Register."""

    name = "middle_east_company_register_spider"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        pass
