from __future__ import annotations

from business_intel_scraper.backend.security.auth import verify_token


def test_verify_token_accepts_non_empty() -> None:
    assert verify_token("token123")


def test_verify_token_rejects_empty() -> None:
    assert not verify_token("")
