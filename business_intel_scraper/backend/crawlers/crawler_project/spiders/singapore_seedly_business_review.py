import scrapy


class SingaporeSeedlyBusinessReviewSpider(scrapy.Spider):
    name = "singapore_seedly_business_review"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
