"""Placeholder spider for UK Electoral Commission Company Donor."""

import scrapy


class UkElectoralCommissionCompanyDonorSpider(scrapy.Spider):
    name = "uk_electoral_commission_company_donor"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
