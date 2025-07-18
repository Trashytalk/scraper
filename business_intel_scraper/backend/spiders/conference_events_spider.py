"""Extract event schedules or attendee lists from conference websites."""

from __future__ import annotations

import scrapy


class ConferenceEventsSpider(scrapy.Spider):
    """Extract event schedules or attendee lists from conference websites."""

    name = "conference_events_spider"
