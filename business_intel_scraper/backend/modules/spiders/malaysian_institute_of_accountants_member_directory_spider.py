"""Placeholder spider for Malaysian Institute of Accountants Member Directory."""

import scrapy


class MalaysianInstituteOfAccountantsMemberDirectorySpider(scrapy.Spider):
    name = "malaysian_institute_of_accountants_member_directory"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
