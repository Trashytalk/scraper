import scrapy


class UaeCentralBankMoneyTransferAgentSpider(scrapy.Spider):
    name = "uae_central_bank_money_transfer_agent"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
