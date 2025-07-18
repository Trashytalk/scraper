"""Collect business, import/export, or industry-specific licenses from
government portals."""

from __future__ import annotations

import scrapy


class PermitsLicensingSpider(scrapy.Spider):
    """Collect business, import/export, or industry-specific licenses from
    government portals."""

    name = "permits_and_licensing_spider"
