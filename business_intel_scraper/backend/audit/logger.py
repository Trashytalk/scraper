"""Simple job event logger writing to the database."""

from __future__ import annotations

import logging
from typing import Optional

from ..db.utils import SessionLocal
from ..db.models import JobEvent

logger = logging.getLogger(__name__)


def _log(job_id: str, event: str, message: Optional[str] = None) -> None:
    """Persist a :class:`JobEvent` record."""
    session = SessionLocal()
    try:
        entry = JobEvent(job_id=job_id, event=event, message=message)
        session.add(entry)
        session.commit()
    except Exception:  # pragma: no cover - unexpected DB failure
        session.rollback()
        logger.exception("Failed to log event %s for job %s", event, job_id)
    finally:
        session.close()


def log_job_start(job_id: str, message: Optional[str] = None) -> None:
    """Record job start."""
    _log(job_id, "start", message)


def log_job_finish(job_id: str, message: Optional[str] = None) -> None:
    """Record job completion."""
    _log(job_id, "finish", message)


def log_job_error(job_id: str, message: Optional[str] = None) -> None:
    """Record a job error."""
    _log(job_id, "error", message)
