"""Spider gathering insurance certificate disclosures."""

from __future__ import annotations

import scrapy


class InsuranceCertificateSpider(scrapy.Spider):
    """Collect business liability or cyber insurance filings."""

    name = "insurance_certificate"

    def parse(self, response: scrapy.http.Response):
        yield {}
