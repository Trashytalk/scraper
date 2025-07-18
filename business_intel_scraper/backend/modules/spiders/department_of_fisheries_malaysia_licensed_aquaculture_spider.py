"""Placeholder spider for Department of Fisheries Malaysia Licensed Aquaculture."""

import scrapy


class DepartmentOfFisheriesMalaysiaLicensedAquacultureSpider(scrapy.Spider):
    name = "department_of_fisheries_malaysia_licensed_aquaculture"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
