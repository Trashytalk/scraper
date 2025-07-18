"""Placeholder spider for SoftBank Vision Fund Global Portfolio."""

import scrapy


class SoftbankVisionFundGlobalPortfolioSpider(scrapy.Spider):
    name = "softbank_vision_fund_global_portfolio"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
