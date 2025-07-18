import scrapy


class SingaporeImdaInnovationAwardWinnerSpider(scrapy.Spider):
    name = "singapore_imda_innovation_award_winner"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
