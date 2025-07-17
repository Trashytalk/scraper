"""Background task worker using Celery."""

from __future__ import annotations

try:
    from celery import Celery
except ModuleNotFoundError:  # pragma: no cover - optional dependency

    class Celery:  # type: ignore
        """Fallback Celery replacement."""

        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def config_from_object(self, *args: object, **kwargs: object) -> None:
            return None

        def task(self, func):  # type: ignore[no-untyped-def]
            return func

celery_app = Celery("business_intel_scraper")

try:  # pragma: no cover - optional dependency
    celery_app.config_from_object(
        "business_intel_scraper.backend.workers.celery_config", namespace="CELERY"
    )
except ModuleNotFoundError:
    pass


@celery_app.task
def example_task(x: int, y: int) -> int:
    """Add two numbers together.

    Parameters
    ----------
    x : int
        First number.
    y : int
        Second number.

    Returns
    -------
    int
        Sum of ``x`` and ``y``.
    """
    return x + y
