"""Track newly registered or expired domains linked to target companies (WHOIS,
DNS data)."""

from __future__ import annotations

import scrapy


class DomainRegistrationSpider(scrapy.Spider):
    """Track newly registered or expired domains linked to target companies (WHOIS,
    DNS data)."""

    name = "domain_registration_spider"
