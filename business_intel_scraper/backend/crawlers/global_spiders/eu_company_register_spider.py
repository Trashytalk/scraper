"""EU Company Register Spider implementation."""

import scrapy


class EuCompanyRegisterSpider(scrapy.Spider):
    """Spider for EU Company Register."""

    name = "eu_company_register_spider"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        pass
