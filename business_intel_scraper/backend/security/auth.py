"""Authentication and authorization helpers."""

from __future__ import annotations

def verify_token(token: str) -> bool:
    """Simple token validation used in tests."""

    return bool(token)
