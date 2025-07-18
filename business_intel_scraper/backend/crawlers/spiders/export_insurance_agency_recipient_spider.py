from __future__ import annotations

import scrapy


class ExportInsuranceAgencyRecipientSpider(scrapy.Spider):
    """Export insurance or guarantee agency recipients."""

    name = "export_insurance_agency_recipient"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        """Parse the response."""
        return {}
