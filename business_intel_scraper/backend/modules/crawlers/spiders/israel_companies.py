"""Monitor the Israeli corporate registry."""

import scrapy


class IsraelCompaniesSpider(scrapy.Spider):
    """Monitor the Israeli corporate registry."""

    name = "israelcompaniesspider"
    allowed_domains = ["justice.gov.il"]
    start_urls = ["https://justice.gov.il"]

    def parse(self, response: scrapy.http.Response) -> dict[str, str]:
        return {"url": response.url}
