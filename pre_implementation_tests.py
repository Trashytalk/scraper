#!/usr/bin/env python3
"""
Pre-Implementation Error Testing Suite
Comprehensive testing before real-world deployment
"""

import os
import sys
import asyncio
import importlib
import traceback
import subprocess
from pathlib import Path
from typing import List, Dict, Any

class PreImplementationTester:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed_tests = []
        
    def log_error(self, test_name: str, error: str):
        self.errors.append(f"❌ {test_name}: {error}")
        
    def log_warning(self, test_name: str, warning: str):
        self.warnings.append(f"⚠️  {test_name}: {warning}")
        
    def log_success(self, test_name: str):
        self.passed_tests.append(f"✅ {test_name}")

    async def test_critical_imports(self):
        """Test all critical imports to catch missing dependencies"""
        critical_imports = [
            # Core framework imports
            ("FastAPI Core", "fastapi", "FastAPI"),
            ("SQLAlchemy", "sqlalchemy", "create_engine"),
            ("Async SQLAlchemy", "sqlalchemy.ext.asyncio", "create_async_engine"),
            ("Pydantic", "pydantic", "BaseModel"),
            ("Redis", "redis", "Redis"),
            
            # Web scraping imports
            ("Requests", "requests", "get"),
            ("BeautifulSoup", "bs4", "BeautifulSoup"),
            ("Selenium", "selenium", "webdriver"),
            ("Playwright", "playwright", "async_api"),
            
            # AI/ML imports
            ("OpenAI", "openai", "OpenAI"),
            ("Transformers", "transformers", "pipeline"),
            ("Torch", "torch", "tensor"),
            ("SpaCy", "spacy", "load"),
            
            # Data processing
            ("Pandas", "pandas", "DataFrame"),
            ("NumPy", "numpy", "array"),
            ("Celery", "celery", "Celery"),
            
            # Security and auth
            ("JWT", "jwt", "encode"),
            ("Cryptography", "cryptography.fernet", "Fernet"),
            ("Passlib", "passlib.hash", "bcrypt"),
            
            # Database drivers
            ("PostgreSQL Driver", "psycopg2", "connect"),
            ("SQLite Async", "aiosqlite", "connect"),
        ]
        
        for test_name, module_name, attr_name in critical_imports:
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, attr_name):
                    self.log_success(f"Import {test_name}")
                else:
                    self.log_warning(f"Import {test_name}", f"Missing attribute {attr_name}")
            except ImportError as e:
                self.log_error(f"Import {test_name}", str(e))
            except Exception as e:
                self.log_error(f"Import {test_name}", f"Unexpected error: {e}")

    async def test_database_configuration(self):
        """Test database configuration and connections"""
        try:
            from business_intel_scraper.database.config import (
                get_async_session, init_database, check_database_health,
                ASYNC_DATABASE_URL, SYNC_DATABASE_URL
            )
            
            # Test URL configuration
            if ASYNC_DATABASE_URL and SYNC_DATABASE_URL:
                self.log_success("Database URL Configuration")
            else:
                self.log_error("Database URL Configuration", "Missing database URLs")
            
            # Test database initialization
            await init_database()
            self.log_success("Database Initialization")
            
            # Test health check
            health = await check_database_health()
            if health.get("status") == "healthy":
                self.log_success("Database Health Check")
            else:
                self.log_error("Database Health Check", health.get("error", "Unknown error"))
                
        except Exception as e:
            self.log_error("Database Configuration", str(e))

    async def test_api_components(self):
        """Test API components and FastAPI setup"""
        try:
            # Test main API app
            from business_intel_scraper.backend.api.main import app
            self.log_success("FastAPI App Import")
            
            # Test API routes
            from business_intel_scraper.backend.api import auth, metrics, notifications
            self.log_success("API Routes Import")
            
            # Test schemas
            from business_intel_scraper.backend.api.schemas import UserCreate, EntityResponse
            self.log_success("API Schemas Import")
            
        except ImportError as e:
            self.log_error("API Components", f"Import error: {e}")
        except Exception as e:
            self.log_error("API Components", str(e))

    def test_file_structure_integrity(self):
        """Test file structure and required files"""
        required_files = [
            "requirements.txt",
            "setup.py",
            ".env.example",
            "business_intel_scraper/__init__.py",
            "business_intel_scraper/backend/api/main.py",
            "business_intel_scraper/database/config.py",
            "business_intel_scraper/database/models.py",
        ]
        
        for file_path in required_files:
            if Path(file_path).exists():
                self.log_success(f"File Structure: {file_path}")
            else:
                self.log_error(f"File Structure: {file_path}", "File not found")

    async def test_environment_configuration(self):
        """Test environment configuration"""
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            # Check critical environment variables
            env_vars = [
                ("DATABASE_URL", "Database connection"),
                ("SECRET_KEY", "API security"),
                ("REDIS_URL", "Cache configuration"),
            ]
            
            for var_name, description in env_vars:
                value = os.getenv(var_name)
                if value:
                    self.log_success(f"Environment: {var_name}")
                else:
                    self.log_warning(f"Environment: {var_name}", f"Missing {description}")
                    
        except Exception as e:
            self.log_error("Environment Configuration", str(e))

    def test_docker_configuration(self):
        """Test Docker configuration files"""
        docker_files = [
            "Dockerfile",
            "docker-compose.yml", 
            "Dockerfile.production",
        ]
        
        for docker_file in docker_files:
            if Path(docker_file).exists():
                self.log_success(f"Docker: {docker_file}")
                # Test file content
                try:
                    with open(docker_file, 'r') as f:
                        content = f.read()
                        if 'requirements.txt' in content:
                            self.log_success(f"Docker Requirements Reference: {docker_file}")
                        else:
                            self.log_warning(f"Docker Requirements Reference: {docker_file}", 
                                           "No requirements.txt reference found")
                except Exception as e:
                    self.log_warning(f"Docker Content: {docker_file}", str(e))
            else:
                self.log_error(f"Docker: {docker_file}", "File not found")

    async def test_scraping_components(self):
        """Test web scraping components"""
        try:
            # Test browser automation
            from business_intel_scraper.backend.browser.playwright_utils import PlaywrightManager
            self.log_success("Playwright Utils Import")
            
            # Test integrations
            from business_intel_scraper.backend.integrations import (
                crawl4ai_wrapper, katana_wrapper
            )
            self.log_success("Scraping Integrations Import")
            
        except ImportError as e:
            self.log_error("Scraping Components", f"Import error: {e}")
        except Exception as e:
            self.log_error("Scraping Components", str(e))

    def test_security_components(self):
        """Test security and authentication components"""
        try:
            from business_intel_scraper.backend.security.auth import AuthManager
            from business_intel_scraper.backend.security.rate_limit import RateLimiter
            from business_intel_scraper.backend.security.captcha import CaptchaHandler
            
            self.log_success("Security Components Import")
            
        except ImportError as e:
            self.log_error("Security Components", f"Import error: {e}")
        except Exception as e:
            self.log_error("Security Components", str(e))

    def test_cli_interface(self):
        """Test CLI interface"""
        try:
            # Test main CLI
            result = subprocess.run([sys.executable, "bis.py", "--help"], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.log_success("CLI Interface")
            else:
                self.log_error("CLI Interface", f"Exit code: {result.returncode}")
                
        except subprocess.TimeoutExpired:
            self.log_error("CLI Interface", "Command timeout")
        except Exception as e:
            self.log_error("CLI Interface", str(e))

    def test_requirements_completeness(self):
        """Test if all requirements are properly specified"""
        try:
            with open('requirements.txt', 'r') as f:
                requirements = f.read()
                
            # Check for critical packages
            critical_packages = [
                'fastapi', 'sqlalchemy', 'pydantic', 'redis', 'celery',
                'requests', 'beautifulsoup4', 'selenium', 'openai',
                'transformers', 'pandas', 'numpy'
            ]
            
            missing_packages = []
            for package in critical_packages:
                if package not in requirements.lower():
                    missing_packages.append(package)
            
            if missing_packages:
                self.log_warning("Requirements Completeness", 
                               f"Potentially missing: {', '.join(missing_packages)}")
            else:
                self.log_success("Requirements Completeness")
                
        except Exception as e:
            self.log_error("Requirements Completeness", str(e))

    async def run_all_tests(self):
        """Run all pre-implementation tests"""
        print("🧪 Starting Pre-Implementation Error Testing...")
        print("=" * 60)
        
        # Run all tests
        await self.test_critical_imports()
        await self.test_database_configuration()
        await self.test_api_components()
        self.test_file_structure_integrity()
        await self.test_environment_configuration()
        self.test_docker_configuration()
        await self.test_scraping_components()
        self.test_security_components()
        self.test_cli_interface()
        self.test_requirements_completeness()
        
        # Print results
        print("\n📊 Test Results Summary:")
        print("=" * 60)
        
        if self.passed_tests:
            print(f"\n✅ PASSED TESTS ({len(self.passed_tests)}):")
            for test in self.passed_tests:
                print(f"  {test}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")
            print(f"\n🚨 {len(self.errors)} errors found - these should be fixed before implementation!")
        else:
            print("\n🎉 No critical errors found!")
            
        print(f"\n📈 Overall Score: {len(self.passed_tests)}/{len(self.passed_tests) + len(self.errors)} tests passed")
        
        return len(self.errors) == 0

async def main():
    """Main testing function"""
    tester = PreImplementationTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🚀 Repository is ready for real implementation testing!")
    else:
        print("\n⚠️  Please fix the errors before proceeding with implementation.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
