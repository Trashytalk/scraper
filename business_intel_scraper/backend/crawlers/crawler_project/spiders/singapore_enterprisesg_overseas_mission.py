import scrapy


class SingaporeEnterprisesgOverseasMissionSpider(scrapy.Spider):
    name = "singapore_enterprisesg_overseas_mission"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
