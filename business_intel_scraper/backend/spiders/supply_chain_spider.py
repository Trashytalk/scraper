"""Harvest supplier information from logistics or trade databases for supply
chain mapping."""

from __future__ import annotations

import scrapy


class SupplyChainSpider(scrapy.Spider):
    """Harvest supplier information from logistics or trade databases for supply
    chain mapping."""

    name = "supply_chain_spider"
