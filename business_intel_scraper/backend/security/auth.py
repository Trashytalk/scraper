"""Authentication helpers."""

from __future__ import annotations


def verify_token(token: str) -> bool:
    """Very basic token check used by tests."""
    return bool(token)
