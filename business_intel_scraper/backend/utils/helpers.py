"""Utility functions for backend logging."""

from __future__ import annotations

import logging
import logging.config
import json
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parents[1] / "logs"
LOG_FILE = LOG_DIR / "app.log"

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

    logging.config.dictConfig(config)
    logger.debug("Logging configured")
