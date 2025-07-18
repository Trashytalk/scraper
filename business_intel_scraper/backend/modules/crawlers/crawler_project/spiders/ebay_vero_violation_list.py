import scrapy


class EbayVeroViolationListSpider(scrapy.Spider):
    name = "ebay_vero_violation_list"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
