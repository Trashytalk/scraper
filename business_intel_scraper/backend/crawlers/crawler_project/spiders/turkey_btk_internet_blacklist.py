import scrapy


class TurkeyBtkInternetBlacklistSpider(scrapy.Spider):
    name = "turkey_btk_internet_blacklist"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
