"""Authentication helpers used in tests."""

from __future__ import annotations


def verify_token(token: str) -> bool:
    """Return ``True`` if ``token`` is a non-empty string."""

    return bool(token)
