"""
Secure Configuration Management for Business Intelligence Scraper
Handles environment variables, security settings, and configuration validation
"""

import os
import secrets
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


class SecurityConfig:
    """Security configuration and validation"""

    # JWT Configuration
    JWT_SECRET: str = os.getenv("JWT_SECRET", secrets.token_urlsafe(32))
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_HOURS: int = int(os.getenv("JWT_EXPIRE_HOURS", "24"))

    # API Security
    API_RATE_LIMIT_PER_MINUTE: int = int(os.getenv("API_RATE_LIMIT_PER_MINUTE", "60"))
    API_RATE_LIMIT_BURST: int = int(os.getenv("API_RATE_LIMIT_BURST", "100"))

    # CORS Configuration
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000"
    ).split(",")

    # Security Headers
    ENABLE_SECURITY_HEADERS: bool = (
        os.getenv("ENABLE_SECURITY_HEADERS", "true").lower() == "true"
    )
    HSTS_MAX_AGE: int = int(os.getenv("HSTS_MAX_AGE", "31536000"))

    @classmethod
    def validate_jwt_secret(cls) -> bool:
        """Validate JWT secret strength"""
        if len(cls.JWT_SECRET) < 32:
            print(
                "⚠️  WARNING: JWT secret is less than 32 characters. Consider using a stronger secret."
            )
            return False
        if (
            cls.JWT_SECRET
            == "your-super-secret-jwt-key-change-this-in-production-min-32-chars"
        ):
            print("⚠️  WARNING: Using default JWT secret. Change this in production!")
            return False
        return True

    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production mode"""
        return os.getenv("DEBUG", "false").lower() == "false"


class DatabaseConfig:
    """Database configuration"""

    DATABASE_PATH: str = os.getenv(
        "DATABASE_PATH", "/home/homebrew/scraper/data/scraper.db"
    )
    DB_CONNECTION_TIMEOUT: int = int(os.getenv("DB_CONNECTION_TIMEOUT", "30"))
    DB_MAX_CONNECTIONS: int = int(os.getenv("DB_MAX_CONNECTIONS", "20"))

    @classmethod
    def get_database_url(cls) -> str:
        """Get SQLite database URL"""
        return f"sqlite:///{cls.DATABASE_PATH}"


class ServerConfig:
    """Server configuration"""

    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")


class ScrapingConfig:
    """Scraping configuration"""

    DEFAULT_REQUEST_TIMEOUT: int = int(os.getenv("DEFAULT_REQUEST_TIMEOUT", "30"))
    MAX_CONCURRENT_JOBS: int = int(os.getenv("MAX_CONCURRENT_JOBS", "10"))
    USER_AGENT: str = os.getenv("USER_AGENT", "BusinessIntelligenceScraper/1.0")


def validate_configuration():
    """Validate all configuration settings"""
    print("🔧 Validating configuration...")

    # Validate security settings
    if not SecurityConfig.validate_jwt_secret():
        print("❌ JWT secret validation failed")
    else:
        print("✅ JWT secret is secure")

    # Check if running in debug mode in production
    if SecurityConfig.is_production() and ServerConfig.DEBUG:
        print("⚠️  WARNING: Debug mode is enabled in production!")

    # Validate database path
    db_dir = Path(DatabaseConfig.DATABASE_PATH).parent
    if not db_dir.exists():
        print(f"📁 Creating database directory: {db_dir}")
        db_dir.mkdir(parents=True, exist_ok=True)

    # Check CORS origins
    if SecurityConfig.is_production():
        for origin in SecurityConfig.CORS_ORIGINS:
            if "localhost" in origin:
                print(f"⚠️  WARNING: Localhost CORS origin in production: {origin}")

    print("✅ Configuration validation complete")


def generate_secure_jwt_secret() -> str:
    """Generate a cryptographically secure JWT secret"""
    return secrets.token_urlsafe(32)


# Export configuration instances
security_config = SecurityConfig()
database_config = DatabaseConfig()
server_config = ServerConfig()
scraping_config = ScrapingConfig()

if __name__ == "__main__":
    print("🔐 Business Intelligence Scraper - Security Configuration")
    print("=" * 60)

    validate_configuration()

    print("\n📋 Current Configuration:")
    print(f"   Database: {database_config.DATABASE_PATH}")
    print(f"   Server: {server_config.HOST}:{server_config.PORT}")
    print(f"   Debug Mode: {server_config.DEBUG}")
    print(f"   CORS Origins: {', '.join(security_config.CORS_ORIGINS)}")
    print(f"   Rate Limit: {security_config.API_RATE_LIMIT_PER_MINUTE}/min")
    print(f"   Security Headers: {security_config.ENABLE_SECURITY_HEADERS}")

    if not SecurityConfig.validate_jwt_secret():
        print("\n🔑 Generate new JWT secret with:")
        print(f"   JWT_SECRET={generate_secure_jwt_secret()}")
