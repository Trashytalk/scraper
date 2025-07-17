import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
)

from business_intel_scraper.backend.db.pipeline import normalize_names


def test_normalize_names() -> None:
    names = ["Acme", "Beta", "Acme", "  Beta  ", "Gamma", ""]
    assert normalize_names(names) == ["Acme", "Beta", "Gamma"]
