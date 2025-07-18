"""Spider for Singapore Official Assignee Bankruptcy Notices (placeholder)."""

import scrapy


class SingaporeOfficialAssigneeBankruptcyNoticesSpider(scrapy.Spider):
    """Placeholder spider for Singapore Official Assignee Bankruptcy Notices."""

    name = "singaporeofficialassigneebankruptcynotices"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
