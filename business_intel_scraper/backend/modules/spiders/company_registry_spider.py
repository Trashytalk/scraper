"""Crawl official government or regional business registries for company
metadata."""

from __future__ import annotations

import scrapy


class CompanyRegistrySpider(scrapy.Spider):
    """Crawl official government or regional business registries for company
    metadata."""

    name = "company_registry_spider"
