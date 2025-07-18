import scrapy


class PolandInfoshareStartupContestWinnerSpider(scrapy.Spider):
    name = "poland_infoshare_startup_contest_winner"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
