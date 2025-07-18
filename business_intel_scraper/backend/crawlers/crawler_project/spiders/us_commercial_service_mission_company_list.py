import scrapy


class UsCommercialServiceMissionCompanyListSpider(scrapy.Spider):
    name = "us_commercial_service_mission_company_list"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
