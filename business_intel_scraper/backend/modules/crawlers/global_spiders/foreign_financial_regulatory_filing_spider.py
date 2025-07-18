"""Foreign Financial Regulatory Filing Spider implementation."""

import scrapy


class ForeignFinancialRegulatoryFilingSpider(scrapy.Spider):
    """Spider for Foreign Financial Regulatory Filing."""

    name = "foreign_financial_regulatory_filing_spider"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        pass
