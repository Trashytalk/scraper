"""Placeholder spider for Turkey TUBITAK Grant Winner."""

import scrapy


class TurkeyTubitakGrantWinnerSpider(scrapy.Spider):
    name = "turkey_tubitak_grant_winner"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
