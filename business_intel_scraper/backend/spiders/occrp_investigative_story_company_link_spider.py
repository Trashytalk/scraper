"""Placeholder spider for OCCRP Investigative Story Company Link."""

import scrapy


class OccrpInvestigativeStoryCompanyLinkSpider(scrapy.Spider):
    name = "occrp_investigative_story_company_link"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
