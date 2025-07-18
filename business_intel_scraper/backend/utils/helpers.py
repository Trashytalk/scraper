"""Utility functions for backend logging."""

from __future__ import annotations

import logging
import logging.config
import json
import os
from pathlib import Path

import requests

LOG_DIR = Path(__file__).resolve().parents[1] / "logs"
LOG_FILE = LOG_DIR / "app.log"
LOG_FORWARD_URL = os.getenv("LOG_FORWARD_URL", "")

logger = logging.getLogger(__name__)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            data["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(data)


class HTTPLogHandler(logging.Handler):
    """Send log records as JSON to ``LOG_FORWARD_URL`` if configured."""

    def __init__(self, url: str, timeout: int = 5) -> None:
        super().__init__()
        self.url = url
        self.timeout = timeout

    def emit(self, record: logging.LogRecord) -> None:  # type: ignore[override]
        try:
            payload = self.format(record)
            requests.post(
                self.url,
                data=payload.encode(),
                headers={"Content-Type": "application/json"},
                timeout=self.timeout,
            )
        except Exception:
            self.handleError(record)


def setup_logging(
    level: int = logging.INFO,
    log_file: str | Path = LOG_FILE,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
) -> None:
    """Configure application logging.

    Parameters
    ----------
    level : int, optional
        Logging level, by default ``logging.INFO``.
    log_file : str | Path, optional
        Path to the log file, by default ``"logs/backend.log"``.
    max_bytes : int, optional
        Maximum bytes before rotating the log file, by default ``10 * 1024 * 1024``.
    backup_count : int, optional
        Number of rotated log files to keep, by default ``5``.
    """

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    config = {
        "version": 1,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
            "json": {
                "()": JsonFormatter,
            },
        },
        "handlers": {
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": str(log_path),
                "maxBytes": max_bytes,
                "backupCount": backup_count,
                "formatter": "json",
            },
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
        },
        "root": {
            "level": level,
            "handlers": ["file", "console"],
        },
    }

    if LOG_FORWARD_URL:
        config["handlers"]["http"] = {
            "class": "business_intel_scraper.backend.utils.helpers.HTTPLogHandler",
            "level": level,
            "url": LOG_FORWARD_URL,
            "formatter": "json",
        }
        config["root"]["handlers"].append("http")

    logging.config.dictConfig(config)
    logger.debug("Logging configured")
