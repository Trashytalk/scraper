from __future__ import annotations

import pytest

from business_intel_scraper.backend.security import solve_captcha
import requests


def test_solve_captcha_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Solver raises ``NotImplementedError`` when not configured."""
    monkeypatch.delenv("CAPTCHA_API_KEY", raising=False)
    with pytest.raises(NotImplementedError):
        solve_captcha(b"dummy")


def test_solve_captcha_with_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    """Solver returns value from mocked HTTP service."""

    class FakeResponse:
        def __init__(self, data: dict[str, str]):
            self._data = data

        def raise_for_status(self) -> None:  # pragma: no cover - simple stub
            pass

        def json(self) -> dict[str, str]:
            return self._data

    def fake_post(url: str, data: dict[str, str], files: dict[str, bytes], timeout: int) -> FakeResponse:
        assert url == "https://mockservice/solve"
        assert "image" in files
        assert data.get("key") == "secret"
        return FakeResponse({"solution": "abcd"})

    monkeypatch.setenv("CAPTCHA_API_KEY", "secret")
    monkeypatch.setenv("CAPTCHA_API_URL", "https://mockservice/solve")
    monkeypatch.setattr(requests, "post", fake_post)

    assert solve_captcha(b"img") == "abcd"
