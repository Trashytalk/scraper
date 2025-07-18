"""Spider watching foreign investment review data."""

from __future__ import annotations

import scrapy


class ForeignInvestmentReviewSpider(scrapy.Spider):
    """Scrape blocked or reviewed transactions."""

    name = "foreign_investment_review"

    def parse(self, response: scrapy.http.Response):
        yield {}
