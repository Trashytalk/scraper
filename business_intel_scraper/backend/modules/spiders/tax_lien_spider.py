"""Extract tax lien and property tax delinquency data for risk analysis."""

from __future__ import annotations

import scrapy


class TaxLienSpider(scrapy.Spider):
    """Extract tax lien and property tax delinquency data for risk analysis."""

    name = "tax_lien_spider"
