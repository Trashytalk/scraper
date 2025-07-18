"""Scrape online business directories for companies in a particular city or
region."""

from __future__ import annotations

import scrapy


class GeographicDirectorySpider(scrapy.Spider):
    """Scrape online business directories for companies in a particular city or
    region."""

    name = "geographic_directory_spider"
