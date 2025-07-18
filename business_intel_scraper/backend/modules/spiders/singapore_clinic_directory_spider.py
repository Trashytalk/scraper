"""Placeholder spider for Singapore Clinic Directory."""

import scrapy


class SingaporeClinicDirectorySpider(scrapy.Spider):
    name = "singapore_clinic_directory"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
