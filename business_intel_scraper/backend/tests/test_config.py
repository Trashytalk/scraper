from __future__ import annotations

import importlib
import os
from pathlib import Path

import pytest
import sys

sys.path.append(str(Path(__file__).resolve().parents[3]))

config = pytest.importorskip("business_intel_scraper.config")


def test_load_env_file(tmp_path: Path, monkeypatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("API_KEY=loaded\n")
    monkeypatch.delenv("API_KEY", raising=False)
    config._load_env_file(env_file)
    assert os.getenv("API_KEY") == "loaded"


def test_settings_reads_env(monkeypatch) -> None:
    monkeypatch.setenv("API_KEY", "from_env")
    module = importlib.reload(config)
    assert module.settings.api_key == "from_env"


def test_https_setting(monkeypatch) -> None:
    monkeypatch.setenv("USE_HTTPS", "true")
    module = importlib.reload(config)
    assert module.settings.use_https is True
