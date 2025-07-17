from __future__ import annotations

from fastapi.testclient import TestClient

from business_intel_scraper.backend.api.main import app

client = TestClient(app)


def test_create_and_read_company() -> None:
    resp = client.post("/companies", json={"name": "Acme"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Acme"
    cid = data["id"]

    get_resp = client.get(f"/companies/{cid}")
    assert get_resp.status_code == 200
    assert get_resp.json() == data

    list_resp = client.get("/companies")
    assert list_resp.status_code == 200
    assert any(item["id"] == cid for item in list_resp.json())
