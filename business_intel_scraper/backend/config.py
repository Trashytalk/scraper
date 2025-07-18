"""Backend application settings."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Configuration loaded from environment variables."""

    api_key: str = ""
    google_api_key: str = ""
    database_url: str = "sqlite:///./development.db"
    proxy_url: str = ""
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    class Config:
        env_file = Path(__file__).resolve().parent / ".env"
        case_sensitive = False


settings = Settings()
