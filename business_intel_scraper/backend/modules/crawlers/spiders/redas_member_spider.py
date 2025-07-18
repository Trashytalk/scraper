from __future__ import annotations

import scrapy


class RedasMemberSpider(scrapy.Spider):
    """Singapore Real Estate Developers’ Association (REDAS) members."""

    name = "redas_member"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
