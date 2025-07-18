from __future__ import annotations

import scrapy


class ThailandBOIIncentiveSpider(scrapy.Spider):
    """Thailand BOI incentive recipients."""

    name = "thailand_boi_incentive"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
