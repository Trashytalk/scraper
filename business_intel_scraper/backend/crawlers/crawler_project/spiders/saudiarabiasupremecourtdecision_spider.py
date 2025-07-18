"""Spider for Saudi Arabia Supreme Court Decision (placeholder)."""

import scrapy


class SaudiArabiaSupremeCourtDecisionSpider(scrapy.Spider):
    """Placeholder spider for Saudi Arabia Supreme Court Decision."""

    name = "saudiarabiasupremecourtdecision"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
