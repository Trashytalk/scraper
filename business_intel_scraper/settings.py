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
class Settings:
    """Container for all application settings."""

    api: APISettings = field(default_factory=APISettings)
    database: DatabaseSettings = field(default_factory=DatabaseSettings)
    proxy: ProxySettings = field(default_factory=ProxySettings)
    rate_limit: RateLimitSettings = field(default_factory=RateLimitSettings)
    require_https: bool = os.getenv("USE_HTTPS", "false").lower() == "true"


settings = Settings()
