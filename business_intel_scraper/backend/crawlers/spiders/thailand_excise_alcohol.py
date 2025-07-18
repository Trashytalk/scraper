"""Scrape Thai excise and alcohol license registries.

Collect data on licensed alcohol, tobacco, and other regulated goods producers.
"""

from __future__ import annotations

import scrapy


class ThailandExciseAlcoholLicenseeSpider(scrapy.Spider):
    """Spider for excise and alcohol licensees."""

    name = "thailandexcisealcohollicenseespider"

    def parse(self, response: scrapy.http.Response):
        """Parse response placeholder."""
        raise NotImplementedError("Spider not implemented yet")
