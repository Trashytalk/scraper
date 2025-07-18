from __future__ import annotations

import scrapy


class AseanInterpolNoticeDirectorSpider(scrapy.Spider):
    """ASEAN Interpol Red/Blue notice company directors."""

    name = "asean_interpol_notice_director"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
