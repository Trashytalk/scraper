"""Placeholder spider for China NDRC JV Approval."""

import scrapy


class ChinaNdrcJvApprovalSpider(scrapy.Spider):
    name = "china_ndrc_jv_approval"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
