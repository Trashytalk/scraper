"""Scrape maritime, aviation, or ground logistics trackers for import/export,
shipments, or asset movements."""

from __future__ import annotations

import scrapy


class LogisticsShippingSpider(scrapy.Spider):
    """Scrape maritime, aviation, or ground logistics trackers for import/export,
    shipments, or asset movements."""

    name = "logistics_and_shipping_spider"
