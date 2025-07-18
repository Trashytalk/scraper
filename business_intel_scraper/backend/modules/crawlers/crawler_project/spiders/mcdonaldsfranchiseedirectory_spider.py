"""Spider for McDonalds Franchisee Directory (placeholder)."""

import scrapy


class McdonaldsFranchiseeDirectorySpider(scrapy.Spider):
    """Placeholder spider for McDonalds Franchisee Directory."""

    name = "mcdonaldsfranchiseedirectory"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
