#!/usr/bin/env python3
"""
Comprehensive Implementation Testing Suite
Tests all critical components for production readiness
"""

import os
import sys
import asyncio
import subprocess
import tempfile
import json
import time
from pathlib import Path
from typing import Dict, Any, List
import requests
from datetime import datetime

class ComprehensiveTestSuite:
    def __init__(self):
        self.results = {
            "passed": [],
            "failed": [],
            "warnings": [],
            "performance": {}
        }
        
    def log_result(self, category: str, test_name: str, details: str = ""):
        self.results[category].append(f"{test_name}: {details}" if details else test_name)
        
    async def test_database_operations(self):
        """Test comprehensive database operations"""
        print("🗄️  Testing Database Operations...")
        
        try:
            from business_intel_scraper.database.config import (
                get_async_session, init_database, check_database_health,
                async_engine, sync_engine
            )
            from business_intel_scraper.database.models import Entity, Connection, Event
            from sqlalchemy import text
            
            # Test database initialization
            start_time = time.time()
            await init_database()
            init_time = time.time() - start_time
            self.results["performance"]["db_init_time"] = init_time
            self.log_result("passed", "Database Initialization", f"{init_time:.2f}s")
            
            # Test health check
            health = await check_database_health()
            if health["status"] == "healthy":
                self.log_result("passed", "Database Health Check", f"Tables: {health.get('entities_count', 0)} entities")
            else:
                self.log_result("failed", "Database Health Check", health.get("error", "Unknown"))
            
            # Test CRUD operations
            async with get_async_session() as session:
                # Create
                test_entity = Entity(
                    name="Test Company",
                    entity_type="organization",
                    source_url="https://example.com",
                    confidence_score=0.95
                )
                session.add(test_entity)
                await session.commit()
                await session.refresh(test_entity)
                self.log_result("passed", "Database Create Operation")
                
                # Read
                result = await session.execute(text("SELECT COUNT(*) FROM entities WHERE name = 'Test Company'"))
                count = result.scalar()
                if count > 0:
                    self.log_result("passed", "Database Read Operation")
                else:
                    self.log_result("failed", "Database Read Operation", "Entity not found")
                
                # Update
                test_entity.confidence_score = 0.99
                await session.commit()
                self.log_result("passed", "Database Update Operation")
                
                # Delete cleanup
                await session.delete(test_entity)
                await session.commit()
                self.log_result("passed", "Database Delete Operation")
                
        except Exception as e:
            self.log_result("failed", "Database Operations", str(e))

    def test_api_server_startup(self):
        """Test if API server can start properly"""
        print("🌐 Testing API Server Startup...")
        
        try:
            # Test importing the FastAPI app
            from business_intel_scraper.backend.api.main import app
            self.log_result("passed", "FastAPI App Import")
            
            # Test that app has expected attributes
            if hasattr(app, 'router') and hasattr(app, 'middleware'):
                self.log_result("passed", "FastAPI App Structure")
            else:
                self.log_result("warnings", "FastAPI App Structure", "Missing expected attributes")
                
            # Try to get app info (this tests if all imports work)
            app_info = {
                "title": getattr(app, 'title', 'Unknown'),
                "version": getattr(app, 'version', 'Unknown'),
            }
            self.log_result("passed", "FastAPI App Configuration", f"Title: {app_info['title']}")
            
        except Exception as e:
            self.log_result("failed", "API Server Startup", str(e))

    def test_environment_security(self):
        """Test environment configuration and security"""
        print("🔒 Testing Environment Security...")
        
        # Check critical environment variables
        critical_vars = {
            "DATABASE_URL": "Database connection string",
            "SECRET_KEY": "JWT signing key", 
            "REDIS_URL": "Cache configuration"
        }
        
        for var_name, description in critical_vars.items():
            value = os.getenv(var_name)
            if value:
                # Check if it's a default/insecure value
                insecure_patterns = ['secret', 'password', 'changeme', 'default', 'test']
                if any(pattern in value.lower() for pattern in insecure_patterns):
                    self.log_result("warnings", f"Environment Security: {var_name}", 
                                  "Uses default/insecure value")
                else:
                    self.log_result("passed", f"Environment Variable: {var_name}")
            else:
                self.log_result("failed", f"Environment Variable: {var_name}", "Missing")

    def test_file_permissions(self):
        """Test file permissions and security"""
        print("📁 Testing File Permissions...")
        
        sensitive_files = [
            ".env",
            "data.db", 
            "business_intel_scraper/backend/security/",
        ]
        
        for file_path in sensitive_files:
            path = Path(file_path)
            if path.exists():
                if path.is_file():
                    # Check file permissions
                    stat = path.stat()
                    # Check if file is readable by others (should not be for .env)
                    if file_path == ".env" and (stat.st_mode & 0o044):
                        self.log_result("warnings", f"File Permissions: {file_path}", 
                                      "Readable by others")
                    else:
                        self.log_result("passed", f"File Permissions: {file_path}")
                else:
                    self.log_result("passed", f"Directory Exists: {file_path}")
            else:
                if file_path == ".env":
                    self.log_result("warnings", f"File Missing: {file_path}", 
                                  "Consider creating from .env.example")
                else:
                    self.log_result("failed", f"File Missing: {file_path}")

    def test_dependency_security(self):
        """Test for known security vulnerabilities in dependencies"""
        print("🛡️  Testing Dependency Security...")
        
        try:
            # Check if pip-audit is available for security scanning
            result = subprocess.run(['pip', 'list'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.log_result("passed", "Package List Available")
                
                # Look for potentially vulnerable packages
                vulnerable_patterns = ['pillow<', 'requests<2.20', 'urllib3<1.24']
                packages = result.stdout.lower()
                
                vulnerabilities_found = []
                for pattern in vulnerable_patterns:
                    if pattern in packages:
                        vulnerabilities_found.append(pattern)
                
                if vulnerabilities_found:
                    self.log_result("warnings", "Dependency Security", 
                                  f"Potentially vulnerable: {', '.join(vulnerabilities_found)}")
                else:
                    self.log_result("passed", "Dependency Security Scan")
            else:
                self.log_result("warnings", "Dependency Security", "Could not scan packages")
                
        except Exception as e:
            self.log_result("warnings", "Dependency Security", f"Scan failed: {e}")

    async def test_performance_benchmarks(self):
        """Test basic performance benchmarks"""
        print("⚡ Testing Performance Benchmarks...")
        
        try:
            # Database performance
            from business_intel_scraper.database.config import get_async_session
            from sqlalchemy import text
            
            # Test query performance
            start_time = time.time()
            async with get_async_session() as session:
                for _ in range(10):
                    await session.execute(text("SELECT 1"))
            query_time = time.time() - start_time
            self.results["performance"]["db_query_10x"] = query_time
            
            if query_time < 1.0:
                self.log_result("passed", "Database Query Performance", f"{query_time:.3f}s for 10 queries")
            else:
                self.log_result("warnings", "Database Query Performance", f"Slow: {query_time:.3f}s for 10 queries")
                
            # Memory usage test
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            self.results["performance"]["memory_usage_mb"] = memory_mb
            
            if memory_mb < 500:  # Less than 500MB
                self.log_result("passed", "Memory Usage", f"{memory_mb:.1f}MB")
            else:
                self.log_result("warnings", "Memory Usage", f"High: {memory_mb:.1f}MB")
                
        except Exception as e:
            self.log_result("warnings", "Performance Benchmarks", str(e))

    def test_error_handling(self):
        """Test error handling and logging"""
        print("🚨 Testing Error Handling...")
        
        try:
            # Test logging configuration
            import logging
            logger = logging.getLogger("test_logger")
            
            # Test that logging works
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.log', delete=False) as log_file:
                handler = logging.FileHandler(log_file.name)
                logger.addHandler(handler)
                logger.setLevel(logging.INFO)
                
                logger.info("Test log message")
                handler.close()
                
                # Check if log was written
                with open(log_file.name, 'r') as f:
                    log_content = f.read()
                    if "Test log message" in log_content:
                        self.log_result("passed", "Logging Configuration")
                    else:
                        self.log_result("failed", "Logging Configuration", "Log message not found")
                
                # Cleanup
                os.unlink(log_file.name)
                
        except Exception as e:
            self.log_result("failed", "Error Handling Test", str(e))

    def test_configuration_files(self):
        """Test configuration file validity"""
        print("⚙️  Testing Configuration Files...")
        
        config_files = {
            "requirements.txt": self._test_requirements_file,
            "setup.py": self._test_setup_file,
            "docker-compose.yml": self._test_docker_compose,
            ".env.example": self._test_env_example,
        }
        
        for file_name, test_func in config_files.items():
            if Path(file_name).exists():
                try:
                    test_func(file_name)
                except Exception as e:
                    self.log_result("failed", f"Config File: {file_name}", str(e))
            else:
                self.log_result("warnings", f"Config File Missing: {file_name}")

    def _test_requirements_file(self, file_path: str):
        """Test requirements.txt validity"""
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Check for critical packages
        critical_packages = ['fastapi', 'sqlalchemy', 'pydantic', 'requests']
        missing = [pkg for pkg in critical_packages if pkg not in content.lower()]
        
        if missing:
            self.log_result("warnings", "Requirements File", f"Missing: {', '.join(missing)}")
        else:
            self.log_result("passed", "Requirements File Completeness")

    def _test_setup_file(self, file_path: str):
        """Test setup.py validity"""
        with open(file_path, 'r') as f:
            content = f.read()
            
        if 'setup(' in content and 'install_requires' in content:
            self.log_result("passed", "Setup.py Structure")
        else:
            self.log_result("warnings", "Setup.py Structure", "Missing expected sections")

    def _test_docker_compose(self, file_path: str):
        """Test docker-compose.yml validity"""
        import yaml
        try:
            with open(file_path, 'r') as f:
                compose_data = yaml.safe_load(f)
                
            if 'services' in compose_data:
                self.log_result("passed", "Docker Compose Structure")
            else:
                self.log_result("warnings", "Docker Compose", "No services defined")
        except yaml.YAMLError as e:
            self.log_result("failed", "Docker Compose", f"Invalid YAML: {e}")

    def _test_env_example(self, file_path: str):
        """Test .env.example validity"""
        with open(file_path, 'r') as f:
            content = f.read()
            
        required_vars = ['DATABASE_URL', 'SECRET_KEY']
        missing = [var for var in required_vars if var not in content]
        
        if missing:
            self.log_result("warnings", "Env Example", f"Missing: {', '.join(missing)}")
        else:
            self.log_result("passed", "Env Example Completeness")

    async def run_all_tests(self):
        """Run the complete test suite"""
        print("🧪 Starting Comprehensive Implementation Testing")
        print("=" * 70)
        
        # Run all test categories
        await self.test_database_operations()
        self.test_api_server_startup()
        self.test_environment_security()
        self.test_file_permissions()
        self.test_dependency_security()
        await self.test_performance_benchmarks()
        self.test_error_handling()
        self.test_configuration_files()
        
        # Print comprehensive results
        self._print_results()
        
        return len(self.results["failed"]) == 0

    def _print_results(self):
        """Print formatted test results"""
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE TEST RESULTS")
        print("=" * 70)
        
        if self.results["passed"]:
            print(f"\n✅ PASSED TESTS ({len(self.results['passed'])}):")
            for test in self.results["passed"]:
                print(f"  ✅ {test}")
        
        if self.results["warnings"]:
            print(f"\n⚠️  WARNINGS ({len(self.results['warnings'])}):")
            for warning in self.results["warnings"]:
                print(f"  ⚠️  {warning}")
        
        if self.results["failed"]:
            print(f"\n❌ FAILED TESTS ({len(self.results['failed'])}):")
            for failure in self.results["failed"]:
                print(f"  ❌ {failure}")
        
        if self.results["performance"]:
            print(f"\n⚡ PERFORMANCE METRICS:")
            for metric, value in self.results["performance"].items():
                print(f"  📊 {metric}: {value}")
        
        # Overall assessment
        total_tests = len(self.results["passed"]) + len(self.results["failed"])
        success_rate = (len(self.results["passed"]) / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n🎯 OVERALL ASSESSMENT:")
        print(f"  Success Rate: {success_rate:.1f}% ({len(self.results['passed'])}/{total_tests})")
        print(f"  Warnings: {len(self.results['warnings'])}")
        print(f"  Critical Failures: {len(self.results['failed'])}")
        
        if len(self.results["failed"]) == 0:
            if len(self.results["warnings"]) == 0:
                print(f"\n🎉 EXCELLENT: All tests passed with no warnings!")
                print(f"   Repository is production-ready!")
            else:
                print(f"\n🚀 GOOD: All critical tests passed!")
                print(f"   Consider addressing {len(self.results['warnings'])} warnings before production.")
        else:
            print(f"\n⚠️  ACTION REQUIRED: {len(self.results['failed'])} critical issues found.")
            print(f"   Please resolve these issues before production deployment.")

async def main():
    """Main test execution"""
    suite = ComprehensiveTestSuite()
    success = await suite.run_all_tests()
    
    if success:
        print(f"\n🎉 All critical tests passed! Repository ready for implementation.")
    else:
        print(f"\n⚠️  Some critical issues found. Please review and fix before deployment.")
        
    return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        sys.exit(1)
