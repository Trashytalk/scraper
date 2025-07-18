import scrapy


class RotterdamPortTerminalOperatorSpider(scrapy.Spider):
    name = "rotterdam_port_terminal_operator"
    allowed_domains: list[str] = []
    start_urls: list[str] = []

    def parse(self, response: scrapy.http.Response) -> None:
        pass
