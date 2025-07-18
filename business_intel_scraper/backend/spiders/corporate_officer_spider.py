"""Extract leadership or executive details from 'About Us' pages for network
analysis."""

from __future__ import annotations

import scrapy


class CorporateOfficerSpider(scrapy.Spider):
    """Extract leadership or executive details from 'About Us' pages for network
    analysis."""

    name = "corporate_officer_spider"
