from __future__ import annotations

import os
import jwt

from business_intel_scraper.backend.security.auth import verify_token


def test_verify_token_accepts_valid() -> None:
    secret = "secret"
    os.environ["JWT_SECRET"] = secret
    os.environ["JWT_ALGORITHM"] = "HS256"
    token = jwt.encode({"sub": "user"}, secret, algorithm="HS256")
    assert verify_token(token)


def test_verify_token_rejects_invalid() -> None:
    os.environ["JWT_SECRET"] = "secret"
    os.environ["JWT_ALGORITHM"] = "HS256"
    assert not verify_token("invalid")
