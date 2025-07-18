"""Collect SEC or similar regulatory filings for detailed financial data."""

from __future__ import annotations

import scrapy


class FinancialFilingsSpider(scrapy.Spider):
    """Collect SEC or similar regulatory filings for detailed financial data."""

    name = "financial_filings_spider"
