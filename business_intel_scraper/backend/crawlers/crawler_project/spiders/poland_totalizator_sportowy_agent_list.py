import scrapy


class PolandTotalizatorSportowyAgentListSpider(scrapy.Spider):
    name = "poland_totalizator_sportowy_agent_list"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
