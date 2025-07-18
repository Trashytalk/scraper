"""Scrape government/commercial procurement tender boards for bid opportunities
and outcomes."""

from __future__ import annotations

import scrapy


class ProcurementBiddingSpider(scrapy.Spider):
    """Scrape government/commercial procurement tender boards for bid opportunities
    and outcomes."""

    name = "procurement_bidding_spider"
