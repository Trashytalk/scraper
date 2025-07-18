"""Spider for India FICCI Member Directory (placeholder)."""

import scrapy


class IndiaFicciMemberDirectorySpider(scrapy.Spider):
    """Placeholder spider for India FICCI Member Directory."""

    name = "indiaficcimemberdirectory"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
