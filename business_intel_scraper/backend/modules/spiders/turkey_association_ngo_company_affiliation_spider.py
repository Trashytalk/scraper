"""Placeholder spider for Turkey Association/NGO Company Affiliation."""

import scrapy


class TurkeyAssociationNgoCompanyAffiliationSpider(scrapy.Spider):
    name = "turkey_association_ngo_company_affiliation"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
