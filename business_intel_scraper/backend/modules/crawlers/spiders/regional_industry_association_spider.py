from __future__ import annotations

import scrapy


class RegionalIndustryAssociationSpider(scrapy.Spider):
    """Regional industry association news and events."""

    name = "regional_industry_association"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
