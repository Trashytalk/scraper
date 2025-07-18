from __future__ import annotations

import scrapy


class EstoniaEResidencyDirectorySpider(scrapy.Spider):
    """Estonia e-Residency company directory."""

    name = "estonia_e_residency_directory"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
