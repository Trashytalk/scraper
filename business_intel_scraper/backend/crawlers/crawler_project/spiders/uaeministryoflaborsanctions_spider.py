"""Spider for UAE Ministry of Labor Sanctions (placeholder)."""

import scrapy


class UaeMinistryOfLaborSanctionsSpider(scrapy.Spider):
    """Placeholder spider for UAE Ministry of Labor Sanctions."""

    name = "uaeministryoflaborsanctions"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
