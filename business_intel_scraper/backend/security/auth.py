"""Authentication helpers used in tests."""

from __future__ import annotations


def verify_token(token: str) -> bool:
    """Basic token validation used in tests."""

    return bool(token)
