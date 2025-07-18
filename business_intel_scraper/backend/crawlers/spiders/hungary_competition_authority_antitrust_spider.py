from __future__ import annotations

import scrapy


class HungaryCompetitionAuthorityAntitrustSpider(scrapy.Spider):
    """Hungary Competition Authority antitrust cases."""

    name = "hungary_competition_authority_antitrust"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
