from pathlib import Path

import requests_cache

from business_intel_scraper.backend.utils.cache import setup_request_cache


def test_setup_request_cache_filesystem(tmp_path, monkeypatch):
    monkeypatch.setenv("CACHE_BACKEND", "filesystem")
    monkeypatch.setenv("CACHE_DIR", str(tmp_path))
    monkeypatch.delenv("CACHE_REDIS_URL", raising=False)
    setup_request_cache()
    cache = requests_cache.get_cache()
    assert isinstance(cache, requests_cache.backends.filesystem.FileCache)
    assert Path(cache.cache_dir).parent == tmp_path
    requests_cache.uninstall_cache()
