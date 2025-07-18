"""Spider for Singapore ACRA business registry."""

import scrapy


class SingaporeACRABusinessRegistrySpider(scrapy.Spider):
    """Scrape company records from ACRA."""

    name = "singapore_acra"
    allowed_domains = ["acra.gov.sg"]
    start_urls = ["https://acra.gov.sg"]

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"url": response.url}
