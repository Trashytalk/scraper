"""Scrape UAE Department of Economic Development registries."""

import scrapy


class UAEDedCompanyRegistrySpider(scrapy.Spider):
    """Scrape UAE Department of Economic Development registries."""

    name = "uaededcompanyregistryspider"
    allowed_domains = ["ded.ae"]
    start_urls = ["https://ded.ae"]

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"url": response.url}
