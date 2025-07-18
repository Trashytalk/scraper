"""Placeholder spider for Singapore GLC Director/Gov Official Overlap."""

import scrapy


class SingaporeGlcDirectorGovOfficialOverlapSpider(scrapy.Spider):
    name = "singapore_glc_director_gov_official_overlap"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
