"""Monitor Vietnam business registrations."""

import scrapy


class VietnamNationalBusinessRegistrySpider(scrapy.Spider):
    """Monitor Vietnam business registrations."""

    name = "vietnamnationalbusinessregistryspider"
    allowed_domains = ["dangkykinhdoanh.gov.vn"]
    start_urls = ["https://dangkykinhdoanh.gov.vn"]

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"url": response.url}
