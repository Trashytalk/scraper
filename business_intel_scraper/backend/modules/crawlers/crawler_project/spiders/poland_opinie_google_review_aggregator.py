import scrapy


class PolandOpinieGoogleReviewAggregatorSpider(scrapy.Spider):
    name = "poland_opinie_google_review_aggregator"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
