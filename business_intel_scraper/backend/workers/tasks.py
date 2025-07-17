"""Background task worker using Celery."""

from __future__ import annotations

try:
    from celery import Celery
except ModuleNotFoundError:  # pragma: no cover - optional dependency

    class Celery:  # type: ignore
        """Fallback Celery replacement."""

        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def task(self, func):  # type: ignore[no-untyped-def]
            return func


celery_app = Celery("tasks")


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
