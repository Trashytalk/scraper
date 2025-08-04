"""
Centralized Logging Configuration
Provides standardized logging across all modules with structured formatting
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"

        return super().format(record)


class StructuredLogger:
    """Centralized logger configuration with structured formatting"""

    def __init__(self, name: str, level: str = "INFO"):
        self.name = name
        self.level = getattr(logging, level.upper())
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Setup logger with consistent formatting"""
        logger = logging.getLogger(self.name)

        # Avoid duplicate handlers
        if logger.handlers:
            return logger

        logger.setLevel(self.level)

        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.level)

        # Structured format
        console_format = ColoredFormatter(
            "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s",
            datefmt="%H:%M:%S",
        )
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)

        # File handler for persistent logging
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        file_handler = logging.FileHandler(
            log_dir / f"{datetime.now().strftime('%Y-%m-%d')}_scraper.log"
        )
        file_handler.setLevel(logging.DEBUG)

        file_format = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

        return logger

    def debug(self, message: str, **kwargs):
        """Debug level logging with context"""
        self.logger.debug(self._format_message(message, **kwargs))

    def info(self, message: str, **kwargs):
        """Info level logging with context"""
        self.logger.info(self._format_message(message, **kwargs))

    def warning(self, message: str, **kwargs):
        """Warning level logging with context"""
        self.logger.warning(self._format_message(message, **kwargs))

    def error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Error level logging with exception details"""
        if error:
            kwargs["error_type"] = type(error).__name__
            kwargs["error_detail"] = str(error)
        self.logger.error(self._format_message(message, **kwargs))

    def critical(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Critical level logging with exception details"""
        if error:
            kwargs["error_type"] = type(error).__name__
            kwargs["error_detail"] = str(error)
        self.logger.critical(self._format_message(message, **kwargs))

    def _format_message(self, message: str, **kwargs) -> str:
        """Format message with additional context"""
        if kwargs:
            context = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
            return f"{message} | {context}"
        return message


def get_logger(name: str, level: Optional[str] = None) -> StructuredLogger:
    """Get a configured logger instance"""
    if level is None:
        level = os.getenv("LOG_LEVEL", "INFO")

    return StructuredLogger(name, level)


def setup_global_logging(level: str = "INFO"):
    """Setup global logging configuration"""
    log_level = getattr(logging, level.upper())

    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s",
        datefmt="%H:%M:%S",
    )

    # Suppress noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


# Global logger instances for common modules
security_logger = get_logger("security")
performance_logger = get_logger("performance")
scraping_logger = get_logger("scraping")
api_logger = get_logger("api")
database_logger = get_logger("database")


# Convenience functions for quick logging
def log_security_event(message: str, **kwargs):
    """Log security-related events"""
    security_logger.info(message, **kwargs)


def log_performance_metric(message: str, **kwargs):
    """Log performance metrics"""
    performance_logger.info(message, **kwargs)


def log_scraping_activity(message: str, **kwargs):
    """Log scraping operations"""
    scraping_logger.info(message, **kwargs)


def log_api_request(message: str, **kwargs):
    """Log API requests and responses"""
    api_logger.info(message, **kwargs)


def log_database_operation(message: str, **kwargs):
    """Log database operations"""
    database_logger.info(message, **kwargs)


def log_error_with_context(logger_name: str, message: str, error: Exception, **kwargs):
    """Log errors with full context"""
    logger = get_logger(logger_name)
    logger.error(message, error=error, **kwargs)


# Initialize global logging on import
setup_global_logging()
