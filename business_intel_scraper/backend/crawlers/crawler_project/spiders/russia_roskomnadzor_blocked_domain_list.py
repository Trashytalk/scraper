import scrapy


class RussiaRoskomnadzorBlockedDomainListSpider(scrapy.Spider):
    name = "russia_roskomnadzor_blocked_domain_list"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
