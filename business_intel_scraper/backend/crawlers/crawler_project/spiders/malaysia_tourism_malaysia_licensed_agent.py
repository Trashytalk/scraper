import scrapy


class MalaysiaTourismMalaysiaLicensedAgentSpider(scrapy.Spider):
    name = "malaysia_tourism_malaysia_licensed_agent"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
