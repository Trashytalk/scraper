"""Harvest seller profiles and product portfolios from Amazon, Alibaba, eBay,
MercadoLibre, etc."""

from __future__ import annotations

import scrapy


class MarketplaceSpider(scrapy.Spider):
    """Harvest seller profiles and product portfolios from Amazon, Alibaba, eBay,
    MercadoLibre, etc."""

    name = "marketplace_spider"
