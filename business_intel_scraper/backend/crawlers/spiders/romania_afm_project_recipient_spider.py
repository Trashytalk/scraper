from __future__ import annotations

import scrapy


class RomaniaAFMProjectRecipientSpider(scrapy.Spider):
    """Romania Environment Fund Admin project recipients."""

    name = "romania_afm_project_recipient"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
