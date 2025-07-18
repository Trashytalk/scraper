"""Spider for Indonesia Forestry Ministry Logging Permit (placeholder)."""

import scrapy


class IndonesiaForestryMinistryLoggingPermitSpider(scrapy.Spider):
    """Placeholder spider for Indonesia Forestry Ministry Logging Permit."""

    name = "indonesiaforestryministryloggingpermit"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response):
        pass
