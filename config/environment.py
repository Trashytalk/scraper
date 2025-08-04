"""
Centralized Configuration Management
Eliminates hardcoded values and provides environment-based configuration
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class EnvironmentConfig:
    """Centralized configuration from environment variables"""

    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "localhost")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))

    # Frontend Configuration
    FRONTEND_HOST: str = os.getenv("FRONTEND_HOST", "localhost")
    FRONTEND_PORT: int = int(os.getenv("FRONTEND_PORT", "5173"))

    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///data.db")

    # Default Credentials (DEVELOPMENT ONLY - change in production)
    DEFAULT_USERNAME: str = os.getenv("DEFAULT_USERNAME", "admin")
    DEFAULT_PASSWORD: str = os.getenv("DEFAULT_PASSWORD", "admin123")

    # Security Configuration
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = int(os.getenv("JWT_EXPIRE_HOURS", "24"))

    # Performance Configuration
    MAX_PAGES_DEFAULT: int = int(os.getenv("MAX_PAGES_DEFAULT", "50"))
    MAX_DEPTH_DEFAULT: int = int(os.getenv("MAX_DEPTH_DEFAULT", "3"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))

    # Monitoring Configuration
    HEALTH_CHECK_INTERVAL: int = int(os.getenv("HEALTH_CHECK_INTERVAL", "60"))
    METRICS_RETENTION_HOURS: int = int(os.getenv("METRICS_RETENTION_HOURS", "24"))

    # Cache Configuration
    CACHE_TTL_SECONDS: int = int(os.getenv("CACHE_TTL_SECONDS", "300"))
    CACHE_MAX_SIZE: int = int(os.getenv("CACHE_MAX_SIZE", "1000"))

    @property
    def API_BASE_URL(self) -> str:
        """Complete API base URL"""
        return f"http://{self.API_HOST}:{self.API_PORT}"

    @property
    def FRONTEND_URL(self) -> str:
        """Complete frontend URL"""
        return f"http://{self.FRONTEND_HOST}:{self.FRONTEND_PORT}"

    @property
    def API_DOCS_URL(self) -> str:
        """API documentation URL"""
        return f"{self.API_BASE_URL}/docs"

    def get_login_credentials(self) -> dict:
        """Get default login credentials for testing"""
        return {"username": self.DEFAULT_USERNAME, "password": self.DEFAULT_PASSWORD}

    def get_auth_headers(self, token: str) -> dict:
        """Get authentication headers"""
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def is_development(self) -> bool:
        """Check if running in development mode"""
        return os.getenv("ENVIRONMENT", "development").lower() == "development"

    def is_production(self) -> bool:
        """Check if running in production mode"""
        return os.getenv("ENVIRONMENT", "development").lower() == "production"


# Global configuration instance
config = EnvironmentConfig()


def get_config() -> EnvironmentConfig:
    """Get the global configuration instance"""
    return config


def get_api_url(endpoint: str = "") -> str:
    """Get complete API URL for an endpoint"""
    base = config.API_BASE_URL
    if endpoint.startswith("/"):
        return f"{base}{endpoint}"
    elif endpoint:
        return f"{base}/{endpoint}"
    return base


def get_test_credentials() -> dict:
    """Get test credentials for automated testing"""
    return config.get_login_credentials()


def get_database_url() -> str:
    """Get database URL"""
    return config.DATABASE_URL


# Environment-specific settings
class DevelopmentConfig(EnvironmentConfig):
    """Development-specific configuration"""

    def __init__(self):
        super().__init__()
        # Override with development-specific values
        self.JWT_SECRET = "dev-secret-key"


class ProductionConfig(EnvironmentConfig):
    """Production-specific configuration"""

    def __init__(self):
        super().__init__()
        # Ensure secure defaults for production
        if self.JWT_SECRET == "your-secret-key-change-in-production":
            raise ValueError("JWT_SECRET must be set in production!")
        if self.DEFAULT_PASSWORD == "admin123":
            raise ValueError("DEFAULT_PASSWORD must be changed in production!")


def get_environment_config() -> EnvironmentConfig:
    """Get environment-specific configuration"""
    env = os.getenv("ENVIRONMENT", "development").lower()

    if env == "production":
        return ProductionConfig()
    else:
        return DevelopmentConfig()
