from __future__ import annotations

import scrapy


class IsraelExportInstituteMemberSpider(scrapy.Spider):
    """Israel Export Institute member directory."""

    name = "israel_export_institute_member"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
