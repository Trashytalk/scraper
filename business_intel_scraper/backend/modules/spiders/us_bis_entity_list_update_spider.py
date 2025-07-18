"""Placeholder spider for US BIS Entity List Update."""

import scrapy


class UsBisEntityListUpdateSpider(scrapy.Spider):
    name = "us_bis_entity_list_update"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
