"""Spider for Malaysia Department of Labor Offender (placeholder)."""

import scrapy


class MalaysiaDepartmentOfLaborOffenderSpider(scrapy.Spider):
    """Placeholder spider for Malaysia Department of Labor Offender."""

    name = "malaysiadepartmentoflaboroffender"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
