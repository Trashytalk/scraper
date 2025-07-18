"""Gather patent or trademark filings to understand new product or technology
areas."""

from __future__ import annotations

import scrapy


class PatentTrademarkSpider(scrapy.Spider):
    """Gather patent or trademark filings to understand new product or technology
    areas."""

    name = "patent_trademark_spider"
