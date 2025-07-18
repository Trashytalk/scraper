"""Placeholder spider for Singapore EDB MoU Partner List."""

import scrapy


class SingaporeEdbMouPartnerListSpider(scrapy.Spider):
    name = "singapore_edb_mou_partner_list"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
