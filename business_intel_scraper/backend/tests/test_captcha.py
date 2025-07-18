from __future__ import annotations

import pytest
import requests

from business_intel_scraper.backend.security import EnvTwoCaptchaSolver, solve_captcha


class FakeResponse:
    def __init__(self, data: dict[str, str]) -> None:
        self._data = data

    def raise_for_status(self) -> None:  # pragma: no cover - simple stub
        pass

    def json(self) -> dict[str, str]:
        return self._data


def test_solve_captcha_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Solver raises ``NotImplementedError`` when not configured."""
    monkeypatch.delenv("CAPTCHA_API_KEY", raising=False)
    with pytest.raises(NotImplementedError):
        solve_captcha(b"dummy")


def test_solve_captcha_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Solver returns value from mocked 2Captcha service."""

    post_calls: list[dict[str, str]] = []
    get_calls: list[dict[str, str]] = []

    def fake_post(url: str, data: dict[str, str], timeout: int) -> FakeResponse:
        post_calls.append({"url": url, **data})
        assert url == "https://mock/in.php"
        assert data["key"] == "secret"
        assert data["method"] == "base64"
        return FakeResponse({"status": 1, "request": "123"})

    responses = iter(
        [
            {"status": 0, "request": "CAPCHA_NOT_READY"},
            {"status": 1, "request": "solved"},
        ]
    )

    def fake_get(url: str, params: dict[str, str], timeout: int) -> FakeResponse:
        get_calls.append({"url": url, **params})
        assert url == "https://mock/res.php"
        return FakeResponse(next(responses))

    monkeypatch.setattr(requests, "post", fake_post)
    monkeypatch.setattr(requests, "get", fake_get)
    monkeypatch.setattr(
        "business_intel_scraper.backend.security.captcha.time.sleep", lambda x: None
    )

    monkeypatch.setenv("CAPTCHA_API_KEY", "secret")
    monkeypatch.setenv("CAPTCHA_API_URL", "https://mock")

    assert solve_captcha(b"img") == "solved"
    assert len(post_calls) == 1
    assert len(get_calls) == 2


def test_solve_captcha_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Solver raises ``ValueError`` when service returns an error."""

    def fake_post(url: str, data: dict[str, str], timeout: int) -> FakeResponse:
        return FakeResponse({"status": 0, "request": "ERROR"})

    monkeypatch.setattr(requests, "post", fake_post)
    monkeypatch.setenv("CAPTCHA_API_KEY", "secret")
    monkeypatch.setenv("CAPTCHA_API_URL", "https://mock")

    with pytest.raises(ValueError):
        solve_captcha(b"img")


def test_env_solver(monkeypatch: pytest.MonkeyPatch) -> None:
    """EnvTwoCaptchaSolver reads configuration from environment."""

    def fake_post(url: str, data: dict[str, str], timeout: int) -> FakeResponse:
        assert data["key"] == "secret"
        return FakeResponse({"status": 1, "request": "123"})

    def fake_get(url: str, params: dict[str, str], timeout: int) -> FakeResponse:
        return FakeResponse({"status": 1, "request": "solved"})

    monkeypatch.setattr(requests, "post", fake_post)
    monkeypatch.setattr(requests, "get", fake_get)
    monkeypatch.setattr(
        "business_intel_scraper.backend.security.captcha.time.sleep", lambda x: None
    )

    monkeypatch.setenv("CAPTCHA_API_KEY", "secret")
    monkeypatch.setenv("CAPTCHA_API_URL", "https://mock")

    solver = EnvTwoCaptchaSolver()
    assert solver.solve(b"img") == "solved"
