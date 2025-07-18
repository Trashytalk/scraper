"""Monitor GCC patent and trademark filings."""

import scrapy


class GCCIPTrademarkRegistrySpider(scrapy.Spider):
    """Monitor GCC patent and trademark filings."""

    name = "gcciptrademarkregistryspider"
    allowed_domains = ["gccpo.org"]
    start_urls = ["https://www.gccpo.org"]

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"url": response.url}
