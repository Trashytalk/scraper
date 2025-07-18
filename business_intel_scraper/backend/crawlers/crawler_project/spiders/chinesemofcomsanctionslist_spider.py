"""Spider for Chinese MOFCOM Sanctions List (placeholder)."""

import scrapy


class ChineseMofcomSanctionsListSpider(scrapy.Spider):
    """Placeholder spider for Chinese MOFCOM Sanctions List."""

    name = "chinesemofcomsanctionslist"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
