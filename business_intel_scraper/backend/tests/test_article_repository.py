from __future__ import annotations

# ruff: noqa: E402

from pathlib import Path
import sys
from datetime import datetime

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from business_intel_scraper.backend.db.repository import (
    ArticleRepository,
    SessionLocal,
    init_db,
)
from business_intel_scraper.backend.db.models import Location
from sqlalchemy.orm import relationship


def test_article_repository_add_and_list() -> None:
    Location.companies = relationship("Company", back_populates="location")
    init_db()
    session = SessionLocal()
    repo = ArticleRepository(session)
    repo.add("Example", "https://example.com", datetime(2025, 7, 18, 0, 0))
    articles = repo.list()
    session.close()
    assert articles and articles[0].title == "Example"
