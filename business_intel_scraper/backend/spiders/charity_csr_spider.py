"""Scrape donations, philanthropic initiatives, or CSR activity for company
social footprint."""

from __future__ import annotations

import scrapy


class CharityCsrSpider(scrapy.Spider):
    """Scrape donations, philanthropic initiatives, or CSR activity for company
    social footprint."""

    name = "charity_csr_spider"
