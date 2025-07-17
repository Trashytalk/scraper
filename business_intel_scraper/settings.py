"""Centralized configuration management for the project."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class APISettings:
    """Settings related to external API access."""

    api_key: str = os.getenv("API_KEY", "")


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
    """Celery task queue configuration."""

    broker_url: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    result_backend: str = os.getenv("CELERY_RESULT_BACKEND", broker_url)


@dataclass
class Settings:
    """Container for all application settings."""

    api: APISettings = field(default_factory=APISettings)
    database: DatabaseSettings = field(default_factory=DatabaseSettings)
    proxy: ProxySettings = field(default_factory=ProxySettings)
    rate_limit: RateLimitSettings = field(default_factory=RateLimitSettings)
    celery: CelerySettings = field(default_factory=CelerySettings)
    require_https: bool = os.getenv("USE_HTTPS", "false").lower() == "true"


settings = Settings()
