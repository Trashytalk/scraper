"""Spider for Singapore Supreme Court Judgment (placeholder)."""

import scrapy


class SingaporeSupremeCourtJudgmentSpider(scrapy.Spider):
    """Placeholder spider for Singapore Supreme Court Judgment."""

    name = "singaporesupremecourtjudgment"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
