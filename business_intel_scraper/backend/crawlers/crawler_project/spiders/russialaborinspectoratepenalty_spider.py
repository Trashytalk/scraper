"""Spider for Russia Labor Inspectorate Penalty (placeholder)."""

import scrapy


class RussiaLaborInspectoratePenaltySpider(scrapy.Spider):
    """Placeholder spider for Russia Labor Inspectorate Penalty."""

    name = "russialaborinspectoratepenalty"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
