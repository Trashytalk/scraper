"""Extract open job postings from major employment boards to gauge hiring
trends."""

from __future__ import annotations

import scrapy


class JobListingsSpider(scrapy.Spider):
    """Extract open job postings from major employment boards to gauge hiring
    trends."""

    name = "job_listings_spider"
