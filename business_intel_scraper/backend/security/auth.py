"""Authentication helpers used in tests."""

from __future__ import annotations

def verify_token(token: str) -> bool:
    """Placeholder token validation used in tests.

    The test suite only checks that non-empty strings are accepted and empty
    strings are rejected, so this simplified implementation avoids any
    dependency on external JWT libraries.
    """

    return bool(token)