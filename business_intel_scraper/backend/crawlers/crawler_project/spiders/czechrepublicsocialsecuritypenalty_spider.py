"""Spider for Czech Republic Social Security Penalty (placeholder)."""

import scrapy


class CzechRepublicSocialSecurityPenaltySpider(scrapy.Spider):
    """Placeholder spider for Czech Republic Social Security Penalty."""

    name = "czechrepublicsocialsecuritypenalty"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
