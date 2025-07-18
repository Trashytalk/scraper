"""Monitor changes to export control/restricted items lists relevant to target
sectors."""

from __future__ import annotations

import scrapy


class ExportControlListSpider(scrapy.Spider):
    """Monitor changes to export control/restricted items lists relevant to target
    sectors."""

    name = "export_control_list_spider"
