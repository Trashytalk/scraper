"""Spider tracking business license revocations."""

from __future__ import annotations

import scrapy


class BusinessLicenseRevocationSpider(scrapy.Spider):
    """Monitor revoked or suspended business licenses."""

    name = "business_license_revocation"

    def parse(self, response: scrapy.http.Response):
        yield {}
