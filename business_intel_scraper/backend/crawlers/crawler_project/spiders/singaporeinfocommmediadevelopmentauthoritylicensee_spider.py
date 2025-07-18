"""Spider for Singapore Infocomm Media Development Authority Licensee.

This is a placeholder implementation.
"""

import scrapy


class SingaporeInfocommMediaDevelopmentAuthorityLicenseeSpider(scrapy.Spider):
    """Placeholder spider for the Infocomm Media Development Authority."""

    name = "singaporeinfocommmediadevelopmentauthoritylicensee"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
