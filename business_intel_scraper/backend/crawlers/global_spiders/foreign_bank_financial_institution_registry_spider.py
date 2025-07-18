"""Foreign Bank/Financial Institution Registry Spider implementation."""

import scrapy


class ForeignBankFinancialInstitutionRegistrySpider(scrapy.Spider):
    """Spider for Foreign Bank/Financial Institution Registry."""

    name = "foreign_bank_financial_institution_registry_spider"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        """Parse the response."""
        pass
