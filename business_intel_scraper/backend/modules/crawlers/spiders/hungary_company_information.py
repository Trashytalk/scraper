"""Scrape business registry for ownership, tax, and compliance flags."""

from __future__ import annotations

import scrapy


class HungaryCompanyInformationServiceSpider(scrapy.Spider):
    """Scrape business registry for ownership, tax, and compliance flags."""

    name = "hungarycompanyinformationservicespider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
