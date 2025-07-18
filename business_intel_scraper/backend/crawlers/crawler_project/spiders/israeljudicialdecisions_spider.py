"""Spider for Israel Judicial Decisions (placeholder)."""

import scrapy


class IsraelJudicialDecisionsSpider(scrapy.Spider):
    """Placeholder spider for Israel Judicial Decisions."""

    name = "israeljudicialdecisions"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
