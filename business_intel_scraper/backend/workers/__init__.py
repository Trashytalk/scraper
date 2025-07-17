"""Celery application setup."""

from __future__ import annotations

import os
from typing import Callable, TypeVar, Any

try:
    from celery import Celery
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    F = TypeVar("F", bound=Callable[..., Any])

    class Celery:  # type: ignore
        """Fallback Celery replacement."""

        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def task(self, func: F) -> F:  # type: ignore[no-untyped-def]
            return func


broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
result_backend = os.getenv("CELERY_RESULT_BACKEND", broker_url)

# Instantiate the Celery application with configured broker and backend
celery_app = Celery("tasks", broker=broker_url, backend=result_backend)

__all__ = ["celery_app"]

