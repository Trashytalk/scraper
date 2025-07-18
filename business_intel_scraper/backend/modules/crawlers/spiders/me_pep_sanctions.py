"""Track sanctions and PEP lists in the Middle East."""

import scrapy


class MiddleEastPEPSanctionsSpider(scrapy.Spider):
    """Track sanctions and PEP lists in the Middle East."""

    name = "middleeastpepsanctionsspider"
    allowed_domains = ["uae.gov.ae"]
    start_urls = ["https://uae.gov.ae"]

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"url": response.url}
