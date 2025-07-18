"""Project-wide configuration settings."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _load_env_file(path: Path) -> None:
    """Load environment variables from ``.env`` if it exists."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key, value)


_load_env_file(Path(__file__).resolve().parent / ".env")


@dataclass
class APISettings:
    """Settings related to external API access."""

    api_key: str = os.getenv("API_KEY", "")
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")


@dataclass
class DatabaseSettings:
    """Database connection settings."""

    url: str = os.getenv("DATABASE_URL", "sqlite:///data.db")


@dataclass
class ProxySettings:
    """Proxy configuration settings."""

    proxy_url: str = os.getenv("PROXY_URL", "")
    rotate: bool = os.getenv("PROXY_ROTATE", "true").lower() == "true"


@dataclass
class RateLimitSettings:
    """Rate limiting configuration settings."""

    limit: int = int(os.getenv("RATE_LIMIT", "60"))
    window: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))


@dataclass
class CelerySettings:
    """Celery broker and backend configuration."""

    broker_url: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    result_backend: str = os.getenv("CELERY_RESULT_BACKEND", broker_url)


@dataclass
class CacheSettings:
    """HTTP request caching settings."""

    backend: str = os.getenv("CACHE_BACKEND", "filesystem")
    expire: int = int(os.getenv("CACHE_EXPIRE", "3600"))
    redis_url: str = os.getenv("CACHE_REDIS_URL", "redis://localhost:6379/1")
    cache_dir: str = os.getenv("CACHE_DIR", "http_cache")


@dataclass
class Settings:
    """Container for all application settings."""

    api: APISettings = field(default_factory=APISettings)
    database: DatabaseSettings = field(default_factory=DatabaseSettings)
    proxy: ProxySettings = field(default_factory=ProxySettings)
    rate_limit: RateLimitSettings = field(default_factory=RateLimitSettings)
    celery: CelerySettings = field(default_factory=CelerySettings)
    cache: CacheSettings = field(default_factory=CacheSettings)
    require_https: bool = os.getenv("USE_HTTPS", "false").lower() == "true"


settings = Settings()
