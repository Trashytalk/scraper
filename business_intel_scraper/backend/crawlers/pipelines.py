"""Scrapy item pipelines."""

from __future__ import annotations

import scrapy


class ExamplePipeline:
    """Pass-through pipeline for demonstration purposes."""

    def process_item(
        self,
        item: scrapy.Item | dict[str, object],
        spider: scrapy.Spider,
    ) -> scrapy.Item | dict[str, object]:
        """Process a scraped item.

        Parameters
        ----------
        item : scrapy.Item | dict[str, object]
            The scraped item to process.
        spider : scrapy.Spider
            The spider which scraped the item.

        Returns
        -------
        scrapy.Item | dict[str, object]
            The unmodified item.
        """
        return item
