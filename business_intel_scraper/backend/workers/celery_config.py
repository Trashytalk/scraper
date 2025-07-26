"""Celery configuration module."""

from __future__ import annotations

from settings import settings

# Broker and backend URLs can be customized via environment variables.
broker_url = settings.celery.broker_url
result_backend = settings.celery.result_backend

# Basic serialization settings
accept_content = ["json"]
result_serializer = "json"
task_serializer = "json"

# Timezone settings
timezone = "UTC"
enable_utc = True

# Scheduled task configuration (Celery Beat)
beat_schedule = {
    "automated-source-discovery": {
        "task": "business_intel_scraper.backend.workers.tasks.scheduled_source_discovery",
        "schedule": 6 * 60 * 60,  # Every 6 hours
        "options": {"expires": 3600},  # Task expires after 1 hour
    },
    "validate-discovered-sources": {
        "task": "business_intel_scraper.backend.workers.tasks.validate_discovered_sources",
        "schedule": 2 * 60 * 60,  # Every 2 hours
        "options": {"expires": 1800},  # Task expires after 30 minutes
    },
    "run-all-spiders": {
        "task": "business_intel_scraper.backend.workers.tasks.scheduled_run_all_spiders",
        "schedule": 12 * 60 * 60,  # Every 12 hours
        "options": {"expires": 3600},  # Task expires after 1 hour
    },
    "generate-marketplace-spiders": {
        "task": "business_intel_scraper.backend.workers.tasks.generate_marketplace_spiders",
        "schedule": 24 * 60 * 60,  # Daily
        "options": {"expires": 3600},  # Task expires after 1 hour
    },
    # Phase 2: DOM Change Detection Tasks
    "check-dom-changes": {
        "task": "business_intel_scraper.backend.workers.tasks.check_dom_changes",
        "schedule": 4 * 60 * 60,  # Every 4 hours
        "options": {"expires": 2400},  # Task expires after 40 minutes
    },
    "update-spider-logic": {
        "task": "business_intel_scraper.backend.workers.tasks.update_spider_logic",
        "schedule": 8 * 60 * 60,  # Every 8 hours
        "options": {"expires": 3600},  # Task expires after 1 hour
    },
    "generate-dom-change-report": {
        "task": "business_intel_scraper.backend.workers.tasks.generate_dom_change_report",
        "schedule": 24 * 60 * 60,  # Daily
        "options": {"expires": 1800},  # Task expires after 30 minutes
    },
}
