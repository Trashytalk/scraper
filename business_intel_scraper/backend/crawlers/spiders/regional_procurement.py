"""Scrape procurement portals across the region."""

import scrapy


class RegionalProcurementSpider(scrapy.Spider):
    """Scrape procurement portals across the region."""

    name = "regionalprocurementspider"
    allowed_domains = ["gebiz.gov.sg"]
    start_urls = ["https://www.gebiz.gov.sg"]

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"url": response.url}
