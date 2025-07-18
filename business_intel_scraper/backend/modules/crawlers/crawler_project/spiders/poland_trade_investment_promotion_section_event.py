import scrapy


class PolandTradeInvestmentPromotionSectionEventSpider(scrapy.Spider):
    name = "poland_trade_investment_promotion_section_event"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
