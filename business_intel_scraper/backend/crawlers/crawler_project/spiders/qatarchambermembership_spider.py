"""Spider for Qatar Chamber Membership (placeholder)."""

import scrapy


class QatarChamberMembershipSpider(scrapy.Spider):
    """Placeholder spider for Qatar Chamber Membership."""

    name = "qatarchambermembership"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
