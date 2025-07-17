"""Authentication and authorization helpers used in tests."""

from __future__ import annotations


def verify_token(token: str) -> bool:
    """Return ``True`` if ``token`` is a non-empty string.

    The real application would verify the JWT using ``PyJWT``. For unit tests we
    simply check that the token is not empty to avoid needing complex fixtures.
    """

    return bool(token)
