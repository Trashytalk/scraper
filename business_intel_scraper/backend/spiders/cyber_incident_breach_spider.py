"""Monitor data breach notification sites, leak forums, or pastebins for company
mentions."""

from __future__ import annotations

import scrapy


class CyberIncidentBreachSpider(scrapy.Spider):
    """Monitor data breach notification sites, leak forums, or pastebins for company
    mentions."""

    name = "cyber_incident_breach_spider"
