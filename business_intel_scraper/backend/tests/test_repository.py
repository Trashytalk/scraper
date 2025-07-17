from __future__ import annotations

# ruff: noqa: E402

from pathlib import Path
import sys

# Ensure package root is on the path when running tests directly from the
# repository checkout.
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from business_intel_scraper.backend.db.repository import (
    CompanyRepository,
    SessionLocal,
    init_db,
)


def test_company_repository_add_and_get(tmp_path):
    """CompanyRepository should persist and retrieve records."""
    # initialize database
    init_db()
    session = SessionLocal()
    repo = CompanyRepository(session)

    company = repo.add("ACME Corp")
    fetched = repo.get(company.id)

    assert fetched is not None
    assert fetched.name == "ACME Corp"
    session.close()
