"""Monitor regional NGO and nonprofit registries."""

import scrapy


class RegionalNGORegistrySpider(scrapy.Spider):
    """Monitor regional NGO and nonprofit registries."""

    name = "regionalngoregistryspider"
    allowed_domains = ["ngoportal.org"]
    start_urls = ["https://ngoportal.org"]

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"url": response.url}
