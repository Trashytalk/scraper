from __future__ import annotations

from fastapi import FastAPI
from fastapi.testclient import TestClient

from business_intel_scraper.backend.security.rate_limit import RateLimitMiddleware


def create_test_app(limit: int = 2) -> TestClient:
    app = FastAPI()
    app.add_middleware(RateLimitMiddleware, limit=limit, window=60)

    @app.get("/")
    async def root() -> dict[str, str]:
        return {"message": "ok"}

    return TestClient(app)


def test_rate_limiter_blocks_after_limit() -> None:
    client = create_test_app(limit=1)
    assert client.get("/").status_code == 200
    second = client.get("/")
    assert second.status_code == 429
