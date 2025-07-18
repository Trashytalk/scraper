"""Gather consumer complaints from BBB, Trustpilot, Ripoff Report, or regional
equivalents."""

from __future__ import annotations

import scrapy


class ConsumerComplaintSpider(scrapy.Spider):
    """Gather consumer complaints from BBB, Trustpilot, Ripoff Report, or regional
    equivalents."""

    name = "consumer_complaint_spider"
