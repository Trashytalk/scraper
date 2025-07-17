from __future__ import annotations

import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
)

from business_intel_scraper.backend.audit.logger import (
    log_job_start,
    log_job_finish,
    log_job_error,
)
from business_intel_scraper.backend.db.utils import init_db, SessionLocal
from business_intel_scraper.backend.db.models import JobEvent


def test_audit_logger_records_events() -> None:
    init_db()
    job_id = "123"
    log_job_start(job_id)
    log_job_finish(job_id)
    log_job_error(job_id, "boom")

    session = SessionLocal()
    events = (
        session.query(JobEvent).filter_by(job_id=job_id).order_by(JobEvent.id).all()
    )
    session.close()
    assert [e.event for e in events] == ["start", "finish", "error"]
    assert events[-1].message == "boom"
