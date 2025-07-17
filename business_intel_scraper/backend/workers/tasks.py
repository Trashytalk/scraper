"""Background task worker using Celery."""

from __future__ import annotations

import time
import uuid
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Dict

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

# In the test environment Celery may not be installed. To provide basic
# asynchronous behaviour without requiring external services we also manage
# a thread pool and in-memory task registry. Each launched task is executed in
# the pool and tracked by a UUID. The API can query the task status using this
# registry.

_executor = ThreadPoolExecutor()
_tasks: Dict[str, Future] = {}


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


def _run_example_spider() -> str:
    """Placeholder function representing a scraping job."""
    time.sleep(1)
    return "scraping complete"


def launch_scraping_task() -> str:
    """Launch a background scraping task.

    Returns
    -------
    str
        Identifier of the launched task.
    """

    task_id = str(uuid.uuid4())
    future = _executor.submit(_run_example_spider)
    _tasks[task_id] = future
    return task_id


def get_task_status(task_id: str) -> str:
    """Return the current status of a task."""

    future = _tasks.get(task_id)
    if future is None:
        return "not_found"
    if future.done():
        return "completed"
    return "running"
