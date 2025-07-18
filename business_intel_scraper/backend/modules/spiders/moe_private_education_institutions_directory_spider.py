"""Placeholder spider for MOE Private Education Institutions Directory."""

import scrapy


class MoePrivateEducationInstitutionsDirectorySpider(scrapy.Spider):
    name = "moe_private_education_institutions_directory"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
