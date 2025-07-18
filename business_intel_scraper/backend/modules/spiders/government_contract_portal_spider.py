"""Harvest awarded contracts and procurement notices for defense or government
spending."""

from __future__ import annotations

import scrapy


class GovernmentContractPortalSpider(scrapy.Spider):
    """Harvest awarded contracts and procurement notices for defense or government
    spending."""

    name = "government_contract_portal_spider"
