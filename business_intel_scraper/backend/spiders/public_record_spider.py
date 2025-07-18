"""Collect publicly available legal records, such as court cases or regulatory
actions."""

from __future__ import annotations

import scrapy


class PublicRecordSpider(scrapy.Spider):
    """Collect publicly available legal records, such as court cases or regulatory
    actions."""

    name = "public_record_spider"
