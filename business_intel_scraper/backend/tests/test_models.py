from __future__ import annotations

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from business_intel_scraper.backend.db.models import Base, User, ScrapeTask  # noqa: E402


def test_user_and_scrape_task_persistence() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        user = User(username="alice", hashed_password="hashed")
        session.add(user)
        session.commit()
        session.refresh(user)

        task = ScrapeTask(user_id=user.id, status="running")
        session.add(task)
        session.commit()
        session.refresh(task)

        fetched_user = session.get(User, user.id)
        fetched_task = session.get(ScrapeTask, task.id)

        assert fetched_user is not None
        assert fetched_user.username == "alice"
        assert fetched_task is not None
        assert fetched_task.user_id == fetched_user.id
        assert fetched_task.status == "running"
