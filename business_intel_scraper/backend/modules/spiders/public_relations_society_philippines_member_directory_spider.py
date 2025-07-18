"""Placeholder spider for PR Society of the Philippines Member Directory."""

import scrapy


class PublicRelationsSocietyPhilippinesMemberDirectorySpider(scrapy.Spider):
    name = "public_relations_society_philippines_member_directory"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
