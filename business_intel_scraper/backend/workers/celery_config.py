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
