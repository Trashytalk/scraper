"""Collect records from the Philippine SEC."""

import scrapy


class PhilippinesSECCompanySpider(scrapy.Spider):
    """Collect records from the Philippine SEC."""

    name = "philippinesseccompanyspider"
    allowed_domains = ["sec.gov.ph"]
    start_urls = ["https://www.sec.gov.ph"]

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"url": response.url}
