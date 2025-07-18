"""Spider for Singapore CPF Compliance Action (placeholder)."""

import scrapy


class SingaporeCpfComplianceActionSpider(scrapy.Spider):
    """Placeholder spider for Singapore CPF Compliance Action."""

    name = "singaporecpfcomplianceaction"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
