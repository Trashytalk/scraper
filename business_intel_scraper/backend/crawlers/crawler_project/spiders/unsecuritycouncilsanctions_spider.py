"""Spider for UN Security Council Sanctions (placeholder)."""

import scrapy


class UnSecurityCouncilSanctionsSpider(scrapy.Spider):
    """Placeholder spider for UN Security Council Sanctions."""

    name = "unsecuritycouncilsanctions"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
