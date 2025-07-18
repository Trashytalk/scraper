"""Spider for Nigeria NEPC Export Licensee (placeholder)."""

import scrapy


class NigeriaNepcExportLicenseeSpider(scrapy.Spider):
    """Placeholder spider for Nigeria NEPC Export Licensee."""

    name = "nigerianepcexportlicensee"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
