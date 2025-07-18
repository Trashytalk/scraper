from __future__ import annotations

import scrapy


class RussiaMOJNGOBusinessLinkSpider(scrapy.Spider):
    """Russia Ministry of Justice NGO business links."""

    name = "russia_moj_ngo_business_link"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
