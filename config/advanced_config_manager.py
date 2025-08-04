#!/usr/bin/env python3
"""
Advanced Configuration Management System
Dynamic configuration with hot-reloading, validation, and environment management
"""

import asyncio
import hashlib
import json
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import redis
import yaml
from pydantic import BaseModel, Field, validator
from watchfiles import awatch

logger = logging.getLogger(__name__)


class ConfigValidationError(Exception):
    """Configuration validation error"""

    pass


class ConfigSection(BaseModel):
    """Base configuration section with validation"""

    class Config:
        extra = "forbid"  # Prevent unknown fields
        validate_assignment = True  # Validate on assignment


class DatabaseConfig(ConfigSection):
    """Database configuration section"""

    url: str = Field(..., description="Database connection URL")
    pool_size: int = Field(default=10, ge=1, le=100, description="Connection pool size")
    pool_timeout: int = Field(default=30, ge=1, description="Pool timeout in seconds")
    echo: bool = Field(default=False, description="Enable SQL logging")
    retry_attempts: int = Field(
        default=3, ge=0, description="Connection retry attempts"
    )

    @validator("url")
    def validate_database_url(cls, v):
        if not v.startswith(("sqlite://", "postgresql://", "mysql://")):
            raise ValueError(
                "Database URL must start with sqlite://, postgresql://, or mysql://"
            )
        return v


class RedisConfig(ConfigSection):
    """Redis configuration section"""

    host: str = Field(default="localhost", description="Redis host")
    port: int = Field(default=6379, ge=1, le=65535, description="Redis port")
    db: int = Field(default=0, ge=0, description="Redis database number")
    password: Optional[str] = Field(default=None, description="Redis password")
    ssl: bool = Field(default=False, description="Enable SSL")
    connection_pool_size: int = Field(
        default=10, ge=1, description="Connection pool size"
    )
    socket_timeout: int = Field(
        default=5, ge=1, description="Socket timeout in seconds"
    )


class SecurityConfig(ConfigSection):
    """Security configuration section"""

    jwt_secret_key: str = Field(..., min_length=32, description="JWT secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expire_minutes: int = Field(default=30, ge=1, description="JWT expiration time")
    password_min_length: int = Field(
        default=8, ge=6, description="Minimum password length"
    )
    max_login_attempts: int = Field(
        default=5, ge=1, description="Maximum login attempts"
    )
    session_timeout_minutes: int = Field(
        default=60, ge=1, description="Session timeout"
    )

    @validator("jwt_secret_key")
    def validate_jwt_secret(cls, v):
        if len(v) < 32:
            raise ValueError("JWT secret key must be at least 32 characters long")
        return v


class RateLimitConfig(ConfigSection):
    """Rate limiting configuration section"""

    default_rate: str = Field(default="100/hour", description="Default rate limit")
    burst_rate: str = Field(default="10/minute", description="Burst rate limit")
    authenticated_multiplier: float = Field(
        default=2.0, ge=1.0, description="Rate multiplier for authenticated users"
    )
    premium_multiplier: float = Field(
        default=5.0, ge=1.0, description="Rate multiplier for premium users"
    )

    @validator("default_rate", "burst_rate")
    def validate_rate_format(cls, v):
        import re

        if not re.match(r"^\d+/(second|minute|hour|day)$", v):
            raise ValueError(
                'Rate must be in format "number/period" (e.g., "100/hour")'
            )
        return v


class MonitoringConfig(ConfigSection):
    """Monitoring and observability configuration"""

    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    metrics_port: int = Field(
        default=9090, ge=1024, le=65535, description="Metrics server port"
    )
    log_level: str = Field(default="INFO", description="Log level")
    log_format: str = Field(default="json", description="Log format")
    trace_sampling_rate: float = Field(
        default=0.1, ge=0.0, le=1.0, description="Trace sampling rate"
    )
    health_check_interval: int = Field(
        default=30, ge=1, description="Health check interval in seconds"
    )

    @validator("log_level")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()


class ScrapingConfig(ConfigSection):
    """Scraping engine configuration"""

    max_concurrent_jobs: int = Field(
        default=10, ge=1, description="Maximum concurrent scraping jobs"
    )
    default_timeout: int = Field(
        default=30, ge=1, description="Default request timeout in seconds"
    )
    max_retries: int = Field(default=3, ge=0, description="Maximum retry attempts")
    user_agent: str = Field(
        default="BusinessIntelScraper/2.0", description="Default user agent"
    )
    respect_robots_txt: bool = Field(default=True, description="Respect robots.txt")
    crawl_delay: float = Field(
        default=1.0, ge=0.1, description="Delay between requests in seconds"
    )
    max_pages_per_job: int = Field(
        default=1000, ge=1, description="Maximum pages per job"
    )


class PerformanceConfig(ConfigSection):
    """Performance optimization configuration"""

    cache_ttl: int = Field(
        default=3600, ge=1, description="Default cache TTL in seconds"
    )
    cache_max_size: int = Field(default=1000, ge=1, description="Maximum cache size")
    worker_processes: int = Field(
        default=4, ge=1, description="Number of worker processes"
    )
    async_timeout: int = Field(default=60, ge=1, description="Async operation timeout")
    batch_size: int = Field(default=100, ge=1, description="Batch processing size")
    memory_limit_mb: int = Field(
        default=512, ge=128, description="Memory limit per worker in MB"
    )


class AppConfig(BaseModel):
    """Main application configuration"""

    app_name: str = Field(
        default="Business Intelligence Scraper", description="Application name"
    )
    version: str = Field(default="2.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(default="development", description="Environment name")

    # Configuration sections
    database: DatabaseConfig
    redis: RedisConfig
    security: SecurityConfig
    rate_limit: RateLimitConfig
    monitoring: MonitoringConfig
    scraping: ScrapingConfig
    performance: PerformanceConfig

    # Custom configuration
    custom: Dict[str, Any] = Field(
        default_factory=dict, description="Custom configuration options"
    )

    class Config:
        validate_assignment = True


class ConfigManager:
    """Advanced configuration manager with hot-reloading and validation"""

    def __init__(
        self,
        config_path: str = "config.yaml",
        environment: Optional[str] = None,
        enable_hot_reload: bool = True,
        redis_client: Optional[redis.Redis] = None,
    ):

        self.config_path = Path(config_path)
        self.environment = environment or os.getenv("ENVIRONMENT", "development")
        self.enable_hot_reload = enable_hot_reload
        self.redis_client = redis_client

        self._config: Optional[AppConfig] = None
        self._config_hash: Optional[str] = None
        self._change_callbacks: List[Callable[[AppConfig], None]] = []
        self._watch_task: Optional[asyncio.Task] = None

        # Environment-specific overrides
        self.env_overrides = self._load_environment_overrides()

    def _load_environment_overrides(self) -> Dict[str, Any]:
        """Load environment-specific configuration overrides"""
        overrides = {}

        # Load from environment variables
        env_mapping = {
            "DATABASE_URL": "database.url",
            "REDIS_HOST": "redis.host",
            "REDIS_PORT": "redis.port",
            "JWT_SECRET_KEY": "security.jwt_secret_key",
            "LOG_LEVEL": "monitoring.log_level",
            "DEBUG": "debug",
            "ENVIRONMENT": "environment",
        }

        for env_var, config_path in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert string values to appropriate types
                if env_var in ["REDIS_PORT"]:
                    value = int(value)
                elif env_var in ["DEBUG"]:
                    value = value.lower() in ("true", "1", "yes", "on")

                # Set nested configuration
                self._set_nested_config(overrides, config_path, value)

        return overrides

    def _set_nested_config(self, config: Dict, path: str, value: Any):
        """Set nested configuration value using dot notation"""
        keys = path.split(".")
        current = config

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value

    def _compute_config_hash(self, config_data: Dict[str, Any]) -> str:
        """Compute hash of configuration data"""
        config_str = json.dumps(config_data, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()

    def _load_config_file(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if not self.config_path.exists():
            logger.warning(
                f"Configuration file {self.config_path} not found, using defaults"
            )
            return {}

        try:
            with open(self.config_path, "r") as f:
                if self.config_path.suffix.lower() in [".yaml", ".yml"]:
                    return yaml.safe_load(f) or {}
                elif self.config_path.suffix.lower() == ".json":
                    return json.load(f)
                else:
                    raise ConfigValidationError(
                        f"Unsupported configuration file format: {self.config_path.suffix}"
                    )

        except Exception as e:
            logger.error(f"Error loading configuration file: {e}")
            raise ConfigValidationError(f"Failed to load configuration: {e}")

    def _merge_configs(
        self, base: Dict[str, Any], override: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge configuration dictionaries recursively"""
        result = base.copy()

        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    async def load_config(self) -> AppConfig:
        """Load and validate configuration"""
        try:
            # Load base configuration
            config_data = self._load_config_file()

            # Apply environment-specific overrides
            config_data = self._merge_configs(config_data, self.env_overrides)

            # Load from Redis if available
            if self.redis_client:
                try:
                    redis_config = await self._load_from_redis()
                    if redis_config:
                        config_data = self._merge_configs(config_data, redis_config)
                except Exception as e:
                    logger.warning(f"Failed to load configuration from Redis: {e}")

            # Validate configuration
            config = AppConfig(**config_data)

            # Update hash
            self._config_hash = self._compute_config_hash(config_data)
            self._config = config

            logger.info(
                f"Configuration loaded successfully (environment: {self.environment})"
            )
            return config

        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            raise ConfigValidationError(f"Invalid configuration: {e}")

    async def _load_from_redis(self) -> Optional[Dict[str, Any]]:
        """Load configuration from Redis"""
        if not self.redis_client:
            return None

        try:
            key = f"config:{self.environment}"
            config_str = await self.redis_client.get(key)

            if config_str:
                return json.loads(config_str)

        except Exception as e:
            logger.warning(f"Failed to load configuration from Redis: {e}")

        return None

    async def save_to_redis(self, config: AppConfig):
        """Save configuration to Redis"""
        if not self.redis_client:
            return

        try:
            key = f"config:{self.environment}"
            config_str = config.json()
            await self.redis_client.setex(key, 3600, config_str)  # 1 hour TTL
            logger.info("Configuration saved to Redis")

        except Exception as e:
            logger.error(f"Failed to save configuration to Redis: {e}")

    def get_config(self) -> AppConfig:
        """Get current configuration"""
        if self._config is None:
            raise RuntimeError("Configuration not loaded. Call load_config() first.")
        return self._config

    def add_change_callback(self, callback: Callable[[AppConfig], None]):
        """Add callback for configuration changes"""
        self._change_callbacks.append(callback)

    def remove_change_callback(self, callback: Callable[[AppConfig], None]):
        """Remove configuration change callback"""
        if callback in self._change_callbacks:
            self._change_callbacks.remove(callback)

    async def _notify_changes(self, new_config: AppConfig):
        """Notify callbacks of configuration changes"""
        for callback in self._change_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(new_config)
                else:
                    callback(new_config)
            except Exception as e:
                logger.error(f"Error in configuration change callback: {e}")

    async def _watch_config_file(self):
        """Watch configuration file for changes"""
        if not self.enable_hot_reload:
            return

        logger.info(f"Watching configuration file: {self.config_path}")

        try:
            async for changes in awatch(self.config_path.parent):
                for change_type, changed_path in changes:
                    if Path(changed_path) == self.config_path:
                        logger.info("Configuration file changed, reloading...")

                        try:
                            new_config = await self.load_config()
                            await self._notify_changes(new_config)
                            logger.info("Configuration reloaded successfully")

                        except Exception as e:
                            logger.error(f"Failed to reload configuration: {e}")

                        break

        except Exception as e:
            logger.error(f"Configuration file watcher error: {e}")

    async def start_watching(self):
        """Start configuration file watching"""
        if self.enable_hot_reload and not self._watch_task:
            self._watch_task = asyncio.create_task(self._watch_config_file())

    async def stop_watching(self):
        """Stop configuration file watching"""
        if self._watch_task:
            self._watch_task.cancel()
            try:
                await self._watch_task
            except asyncio.CancelledError:
                pass
            self._watch_task = None

    @asynccontextmanager
    async def managed_config(self):
        """Context manager for configuration lifecycle"""
        try:
            await self.load_config()
            await self.start_watching()
            yield self.get_config()
        finally:
            await self.stop_watching()

    def update_config(self, updates: Dict[str, Any]) -> AppConfig:
        """Update configuration with new values"""
        if self._config is None:
            raise RuntimeError("Configuration not loaded")

        # Merge updates with current configuration
        current_dict = self._config.dict()
        merged_dict = self._merge_configs(current_dict, updates)

        # Validate new configuration
        new_config = AppConfig(**merged_dict)
        self._config = new_config

        # Save to file
        self._save_config_file(merged_dict)

        return new_config

    def _save_config_file(self, config_data: Dict[str, Any]):
        """Save configuration to file"""
        try:
            with open(self.config_path, "w") as f:
                if self.config_path.suffix.lower() in [".yaml", ".yml"]:
                    yaml.dump(config_data, f, default_flow_style=False)
                elif self.config_path.suffix.lower() == ".json":
                    json.dump(config_data, f, indent=2)

            logger.info(f"Configuration saved to {self.config_path}")

        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise ConfigValidationError(f"Failed to save configuration: {e}")


# Global configuration manager instance
config_manager = ConfigManager()


async def get_config() -> AppConfig:
    """Get application configuration"""
    return config_manager.get_config()


async def init_config(
    config_path: str = "config.yaml",
    environment: Optional[str] = None,
    redis_client: Optional[redis.Redis] = None,
) -> AppConfig:
    """Initialize configuration system"""
    global config_manager
    config_manager = ConfigManager(
        config_path=config_path, environment=environment, redis_client=redis_client
    )

    return await config_manager.load_config()


# Example usage and testing
if __name__ == "__main__":
    import asyncio

    async def config_change_handler(config: AppConfig):
        print(f"Configuration changed! New log level: {config.monitoring.log_level}")

    async def main():
        # Initialize configuration
        config = await init_config("config.yaml")

        # Add change callback
        config_manager.add_change_callback(config_change_handler)

        # Start watching for changes
        await config_manager.start_watching()

        print(f"Configuration loaded:")
        print(f"- Environment: {config.environment}")
        print(f"- Database URL: {config.database.url}")
        print(f"- Redis Host: {config.redis.host}")
        print(f"- Log Level: {config.monitoring.log_level}")

        # Example of updating configuration
        config_manager.update_config({"monitoring": {"log_level": "DEBUG"}})

        # Keep running for demo
        print("Watching for configuration changes... (Ctrl+C to stop)")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("Stopping...")
        finally:
            await config_manager.stop_watching()

    # Run the example
    asyncio.run(main())
