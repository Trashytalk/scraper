import scrapy


class PolandKnfPaymentAgentRegisterSpider(scrapy.Spider):
    name = "poland_knf_payment_agent_register"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
