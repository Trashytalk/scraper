from __future__ import annotations

import scrapy


class SaudiContractorsAuthorityMemberSpider(scrapy.Spider):
    """Saudi Contractors Authority members."""

    name = "saudi_contractors_authority_member"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
