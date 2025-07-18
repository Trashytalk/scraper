import scrapy


class UaeNationalLotteryAgentSpider(scrapy.Spider):
    name = "uae_national_lottery_agent"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
