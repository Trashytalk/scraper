"""Placeholder spider for Singapore Majlis Ugama Islam Singapura Business Arm."""

import scrapy


class SingaporeMajlisUgamaIslamSingapuraBusinessArmSpider(scrapy.Spider):
    name = "singapore_majlis_ugama_islam_singapura_business_arm"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
