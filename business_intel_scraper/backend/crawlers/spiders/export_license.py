"""Spider for export license applications."""

from __future__ import annotations

import scrapy


class ExportLicenseSpider(scrapy.Spider):
    """Scrape export license application lists."""

    name = "export_license"

    def parse(self, response: scrapy.http.Response):
        yield {}
