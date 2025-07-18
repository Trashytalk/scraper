"""Placeholder spider for Russian Maritime Register."""

import scrapy


class RussianMaritimeRegisterSpider(scrapy.Spider):
    name = "russian_maritime_register"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
