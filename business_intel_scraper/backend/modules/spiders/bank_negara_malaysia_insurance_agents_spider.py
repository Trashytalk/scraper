"""Placeholder spider for Bank Negara Malaysia Insurance Agents."""

import scrapy


class BankNegaraMalaysiaInsuranceAgentsSpider(scrapy.Spider):
    name = "bank_negara_malaysia_insurance_agents"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
