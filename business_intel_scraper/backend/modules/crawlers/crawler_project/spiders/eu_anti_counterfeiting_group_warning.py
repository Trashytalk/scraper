import scrapy


class EuAntiCounterfeitingGroupWarningSpider(scrapy.Spider):
    name = "eu_anti_counterfeiting_group_warning"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
