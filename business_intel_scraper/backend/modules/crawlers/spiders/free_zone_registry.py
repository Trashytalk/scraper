"""Track registrations in regional free zones."""

import scrapy


class FreeZoneRegistrySpider(scrapy.Spider):
    """Track registrations in regional free zones."""

    name = "freezoneregistryspider"
    allowed_domains = ["dwtc.com"]
    start_urls = ["https://dwtc.com"]

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"url": response.url}
