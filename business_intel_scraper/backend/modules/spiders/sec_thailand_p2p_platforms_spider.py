"""Placeholder spider for SEC Thailand P2P Platforms."""

import scrapy


class SecThailandP2pPlatformsSpider(scrapy.Spider):
    name = "sec_thailand_p2p_platforms"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        """Parse the response."""
        pass
