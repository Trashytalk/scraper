"""Placeholder spider for Singapore Police Force Security Agency Directory."""

import scrapy


class SingaporePoliceForceSecurityAgencyDirectorySpider(scrapy.Spider):
    name = "singapore_police_force_security_agency_directory"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
