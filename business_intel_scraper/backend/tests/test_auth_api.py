# ruff: noqa: E402
import os

DB_PATH = "./test_auth.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
os.environ["DATABASE_URL"] = f"sqlite:///{DB_PATH}"

from fastapi import FastAPI
from fastapi.testclient import TestClient

from business_intel_scraper.backend.db import engine, SessionLocal
from business_intel_scraper.backend.db.models import Base, User
from business_intel_scraper.backend.api.auth import router, pwd_context

app = FastAPI()
app.include_router(router)
Base.metadata.create_all(bind=engine)
client = TestClient(app)


def test_register_and_login() -> None:
    resp = client.post(
        "/auth/register", json={"username": "alice", "password": "secret"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "alice"

    session = SessionLocal()
    user = session.query(User).filter_by(id=data["id"]).first()
    assert user is not None
    assert user.hashed_password != "secret"
    assert pwd_context.verify("secret", user.hashed_password)
    session.close()

    login = client.post("/auth/login", json={"username": "alice", "password": "secret"})
    assert login.status_code == 200
    assert login.json()["message"] == "Login successful"


def test_login_invalid() -> None:
    resp = client.post("/auth/login", json={"username": "ghost", "password": "secret"})
    assert resp.status_code == 400


def test_duplicate_register() -> None:
    assert (
        client.post(
            "/auth/register", json={"username": "dup", "password": "x"}
        ).status_code
        == 200
    )
    second = client.post("/auth/register", json={"username": "dup", "password": "x"})
    assert second.status_code == 400
