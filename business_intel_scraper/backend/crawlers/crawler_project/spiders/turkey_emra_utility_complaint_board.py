import scrapy


class TurkeyEmraUtilityComplaintBoardSpider(scrapy.Spider):
    name = "turkey_emra_utility_complaint_board"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
