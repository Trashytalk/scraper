"""Placeholder spider for SEDA Malaysia Registered Feed-in Approval Holders."""

import scrapy


class SedaMalaysiaFeedInApprovalHoldersSpider(scrapy.Spider):
    name = "seda_malaysia_feed_in_approval_holders"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
