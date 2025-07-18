import scrapy


class SingaporeSfaFoodSafetyOffenderSpider(scrapy.Spider):
    name = "singapore_sfa_food_safety_offender"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
