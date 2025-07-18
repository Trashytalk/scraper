"""Spider for Vietnam MONRE Permit Issue Revocation (placeholder)."""

import scrapy


class VietnamMonrePermitIssueRevocationSpider(scrapy.Spider):
    """Placeholder spider for Vietnam MONRE Permit Issue Revocation."""

    name = "vietnammonrepermitissuerevocation"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
