"""Track listings on SGX and Bursa Malaysia."""

import scrapy


class SGXBursaListingSpider(scrapy.Spider):
    """Track listings on SGX and Bursa Malaysia."""

    name = "sgxbursalistingspider"
    allowed_domains = ["sgx.com"]
    start_urls = ["https://www.sgx.com"]

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"url": response.url}
