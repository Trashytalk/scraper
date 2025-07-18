"""Collect information on grants or venture capital investments for early-stage
companies."""

from __future__ import annotations

import scrapy


class GrantOrFundingDatabaseSpider(scrapy.Spider):
    """Collect information on grants or venture capital investments for early-stage
    companies."""

    name = "grant_or_funding_database_spider"
