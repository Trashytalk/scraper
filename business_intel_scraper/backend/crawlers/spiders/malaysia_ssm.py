"""Scrape company data from Suruhanjaya Syarikat Malaysia (SSM)."""

import scrapy


class MalaysiaSSMCompanyRegistrySpider(scrapy.Spider):
    """Scrape company data from Suruhanjaya Syarikat Malaysia (SSM)."""

    name = "malaysiassmcompanyregistryspider"
    allowed_domains = ["ssm.com.my"]
    start_urls = ["https://www.ssm.com.my"]

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"url": response.url}
