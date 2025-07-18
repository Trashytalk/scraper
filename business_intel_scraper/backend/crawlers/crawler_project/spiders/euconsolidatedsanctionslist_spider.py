"""Spider for EU Consolidated Sanctions List (placeholder)."""

import scrapy


class EuConsolidatedSanctionsListSpider(scrapy.Spider):
    """Placeholder spider for EU Consolidated Sanctions List."""

    name = "euconsolidatedsanctionslist"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
