"""Monitor vendor security advisories to track incidents or vulnerabilities
affecting key suppliers."""

from __future__ import annotations

import scrapy


class SecurityAdvisorySpider(scrapy.Spider):
    """Monitor vendor security advisories to track incidents or vulnerabilities
    affecting key suppliers."""

    name = "security_advisory_spider"
