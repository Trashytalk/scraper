"""Celery application setup.

This module configures the Celery app used by background workers. The broker
URL and result backend can be provided via the ``CELERY_BROKER_URL`` and
``CELERY_RESULT_BACKEND`` environment variables. If not specified, a local
Redis instance is used.
"""

from __future__ import annotations

import os

try:
    from celery import Celery
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    class Celery:  # type: ignore
        """Fallback Celery replacement."""

        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def task(self, func):  # type: ignore[no-untyped-def]
            return func


broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
result_backend = os.getenv("CELERY_RESULT_BACKEND", broker_url)

# Instantiate the Celery application with configured broker and backend
celery_app = Celery("tasks", broker=broker_url, backend=result_backend)

__all__ = ["celery_app"]

