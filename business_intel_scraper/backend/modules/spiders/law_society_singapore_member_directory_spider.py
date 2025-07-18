"""Placeholder spider for Law Society of Singapore Member Directory."""

import scrapy


class LawSocietySingaporeMemberDirectorySpider(scrapy.Spider):
    name = "law_society_singapore_member_directory"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
