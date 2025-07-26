from __future__ import annotations

# ruff: noqa: E402

import os
import jwt
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("DATABASE_URL", "sqlite:///test.db")

from business_intel_scraper.backend.security.auth import (
    verify_token,
    create_token,
    require_token,
    require_role,
)
from business_intel_scraper.backend.db.models import UserRole


def test_verify_token_accepts_valid() -> None:
    secret = "secret"
    os.environ["JWT_SECRET"] = secret
    os.environ["JWT_ALGORITHM"] = "HS256"
    token = jwt.encode({"sub": "user"}, secret, algorithm="HS256")
    assert verify_token(token)


def test_create_and_require_token() -> None:
    os.environ["JWT_SECRET"] = "secret"
    os.environ["JWT_ALGORITHM"] = "HS256"
    token = create_token("1", UserRole.ADMIN.value)

    app = FastAPI()

    @app.get("/protected", dependencies=[Depends(require_token)])
    def protected():
        return {"ok": True}

    @app.get("/admin", dependencies=[require_role(UserRole.ADMIN)])
    def admin():
        return {"ok": True}

    client = TestClient(app)
    headers = {"Authorization": f"Bearer {token}"}

    assert client.get("/protected", headers=headers).status_code == 200
    assert client.get("/admin", headers=headers).status_code == 200

    # wrong role
    other = create_token("2", UserRole.ANALYST.value)
    resp = client.get("/admin", headers={"Authorization": f"Bearer {other}"})
    assert resp.status_code == 403


def test_verify_token_rejects_invalid() -> None:
    os.environ["JWT_SECRET"] = "secret"
    os.environ["JWT_ALGORITHM"] = "HS256"
    assert not verify_token("invalid")
