"""Extract company and licensing data from AHU and OSS."""

import scrapy


class IndonesiaAHUOSSRegistrySpider(scrapy.Spider):
    """Extract company and licensing data from AHU and OSS."""

    name = "indonesiaahuossregistryspider"
    allowed_domains = ["ahu.go.id"]
    start_urls = ["https://ahu.go.id"]

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"url": response.url}
