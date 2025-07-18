"""Placeholder spider for Singapore Strategic Goods Control Offender."""

import scrapy


class SingaporeStrategicGoodsControlOffenderSpider(scrapy.Spider):
    name = "singapore_strategic_goods_control_offender"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
