from __future__ import annotations

import scrapy


class WeiboChinaBusinessComplaintSpider(scrapy.Spider):
    """Placeholder for the Weibo China Business Complaint."""

    name = "weibo_china_business_complaint_spider"

    def parse(self, response: scrapy.http.Response):
        raise NotImplementedError("Spider not yet implemented")
