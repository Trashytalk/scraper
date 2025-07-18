"""Collect bill of lading, import/export, or customs declaration data."""

from __future__ import annotations

import scrapy


class ImportExportTradeSpider(scrapy.Spider):
    """Collect bill of lading, import/export, or customs declaration data."""

    name = "import_export_trade_spider"
