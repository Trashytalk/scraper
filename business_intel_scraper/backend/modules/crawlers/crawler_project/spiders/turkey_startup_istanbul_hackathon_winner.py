import scrapy


class TurkeyStartupIstanbulHackathonWinnerSpider(scrapy.Spider):
    name = "turkey_startup_istanbul_hackathon_winner"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
