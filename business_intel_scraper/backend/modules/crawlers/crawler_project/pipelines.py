# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy


class CrawlerProjectPipeline:
    def process_item(
        self,
        item: dict[str, object],
        spider: "scrapy.Spider",
    ) -> dict[str, object]:
        return item
