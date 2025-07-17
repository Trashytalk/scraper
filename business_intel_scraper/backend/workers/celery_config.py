"""Celery configuration module."""

from __future__ import annotations

import os

# Broker and backend URLs can be customized via environment variables.
broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Basic serialization settings
accept_content = ["json"]
result_serializer = "json"
task_serializer = "json"

# Timezone settings
timezone = "UTC"
enable_utc = True
