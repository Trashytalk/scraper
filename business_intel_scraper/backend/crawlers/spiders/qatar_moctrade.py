"""Scrape Qatari business registrations."""

import scrapy


class QatarMinistryCommerceSpider(scrapy.Spider):
    """Scrape Qatari business registrations."""

    name = "qatarministrycommercespider"
    allowed_domains = ["moci.gov.qa"]
    start_urls = ["https://www.moci.gov.qa"]

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"url": response.url}
