"""Extract company data from Egypt GAFI."""

import scrapy


class EgyptGAFIRegistrySpider(scrapy.Spider):
    """Extract company data from Egypt GAFI."""

    name = "egyptgafiregistryspider"
    allowed_domains = ["gafi.gov.eg"]
    start_urls = ["https://www.gafi.gov.eg"]

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"url": response.url}
