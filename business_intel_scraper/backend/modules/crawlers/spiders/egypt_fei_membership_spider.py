from __future__ import annotations

import scrapy


class EgyptFEIMembershipSpider(scrapy.Spider):
    """Egypt Federation of Egyptian Industries membership."""

    name = "egypt_fei_membership"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
