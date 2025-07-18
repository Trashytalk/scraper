"""Spider for Thailand Automotive Industry Club Member (placeholder)."""

import scrapy


class ThailandAutomotiveIndustryClubMemberSpider(scrapy.Spider):
    """Placeholder spider for Thailand Automotive Industry Club Member."""

    name = "thailandautomotiveindustryclubmember"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
