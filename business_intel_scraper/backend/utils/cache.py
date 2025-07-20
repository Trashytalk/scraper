"""HTTP request caching helpers."""

from __future__ import annotations

import os
from pathlib import Path

import requests_cache


_DEF_EXPIRE = 3600


def setup_request_cache() -> None:
    """Configure a requests cache using Redis or the filesystem."""

    backend = os.getenv("CACHE_BACKEND", "filesystem").lower()
    expire = int(os.getenv("CACHE_EXPIRE", str(_DEF_EXPIRE)))

    if backend == "redis":
        redis_url = os.getenv("CACHE_REDIS_URL", "redis://localhost:6379/1")
        try:
            from redis import from_url as redis_from_url
        except Exception as exc:  # pragma: no cover - import error tested indirectly
            raise RuntimeError(
                "Redis backend requested but redis package missing"
            ) from exc

        requests_cache.install_cache(
            "bi_cache",
            backend="redis",
            connection=redis_from_url(redis_url),  # type: ignore[no-untyped-call]
            expire_after=expire,
        )
    else:
        cache_dir = Path(os.getenv("CACHE_DIR", "http_cache"))
        cache_dir.mkdir(parents=True, exist_ok=True)
        requests_cache.install_cache(
            str(cache_dir / "requests_cache"),
            backend="filesystem",
            expire_after=expire,
        )
