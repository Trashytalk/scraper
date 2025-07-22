#!/usr/bin/env python3
"""
Setup Validation Script
Run this after following the setup guide to verify your installation
"""

import sys
import os
import subprocess
from pathlib import Path
import asyncio

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def print_step(step, text):
    print(f"\n{step}. {text}")

def check_mark(success, message):
    symbol = "✅" if success else "❌"
    print(f"   {symbol} {message}")
    return success

async def main():
    print_header("🧪 BUSINESS INTELLIGENCE SCRAPER - SETUP VALIDATION")
    
    all_good = True
    
    # Step 1: Python Environment
    print_step("1", "PYTHON ENVIRONMENT")
    
    # Check Python version
    python_version = sys.version_info
    python_ok = python_version.major == 3 and python_version.minor >= 11
    all_good &= check_mark(python_ok, f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check virtual environment
    venv_active = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    all_good &= check_mark(venv_active, f"Virtual environment active: {venv_active}")
    
    # Step 2: File Structure
    print_step("2", "FILE STRUCTURE")
    
    required_files = [
        ".env",
        "requirements.txt", 
        "business_intel_scraper/database/config.py",
        "business_intel_scraper/backend/api/main.py",
        "bis.py"
    ]
    
    for file_path in required_files:
        exists = Path(file_path).exists()
        all_good &= check_mark(exists, f"{file_path}")
    
    # Step 3: Environment Configuration
    print_step("3", "ENVIRONMENT CONFIGURATION")
    
    env_file = Path(".env")
    if env_file.exists():
        # Check file permissions
        import stat
        perms = oct(env_file.stat().st_mode)[-3:]
        perms_ok = perms == "600"
        all_good &= check_mark(perms_ok, f".env file permissions: {perms} (should be 600)")
        
        # Check key environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        database_url = os.getenv("DATABASE_URL")
        secret_key = os.getenv("SECRET_KEY")
        
        all_good &= check_mark(database_url is not None, f"DATABASE_URL configured: {database_url}")
        all_good &= check_mark(secret_key and len(secret_key) >= 32, f"SECRET_KEY configured (length: {len(secret_key) if secret_key else 0})")
    
    # Step 4: Core Dependencies
    print_step("4", "CORE DEPENDENCIES")
    
    try:
        import fastapi
        all_good &= check_mark(True, f"FastAPI: {fastapi.__version__}")
    except ImportError:
        all_good &= check_mark(False, "FastAPI: Not installed")
    
    try:
        import sqlalchemy
        all_good &= check_mark(True, f"SQLAlchemy: {sqlalchemy.__version__}")
    except ImportError:
        all_good &= check_mark(False, "SQLAlchemy: Not installed")
    
    try:
        import uvicorn
        all_good &= check_mark(True, f"Uvicorn: {uvicorn.__version__}")
    except ImportError:
        all_good &= check_mark(False, "Uvicorn: Not installed")
    
    # Step 5: Core Module Imports
    print_step("5", "CORE MODULE IMPORTS")
    
    modules_to_test = [
        ("Database Config", "business_intel_scraper.database.config"),
        ("API Dependencies", "business_intel_scraper.backend.api.dependencies"),
        ("Auth Manager", "business_intel_scraper.backend.security.auth"),
        ("Rate Limiter", "business_intel_scraper.backend.security.rate_limit"),
    ]
    
    for name, module in modules_to_test:
        try:
            __import__(module)
            all_good &= check_mark(True, f"{name}")
        except Exception as e:
            all_good &= check_mark(False, f"{name}: {e}")
    
    # Step 6: Database Connectivity
    print_step("6", "DATABASE CONNECTIVITY")
    
    try:
        from business_intel_scraper.database.config import check_database_health
        health = await check_database_health()
        db_healthy = health.get("status") == "healthy"
        all_good &= check_mark(db_healthy, f"Database health: {health.get('status')}")
        if db_healthy:
            print(f"      Database type: {health.get('database')}")
    except Exception as e:
        all_good &= check_mark(False, f"Database connectivity: {e}")
    
    # Step 7: Essential API Components
    print_step("7", "ESSENTIAL API COMPONENTS")
    
    try:
        from business_intel_scraper.backend.api.dependencies import require_token
        all_good &= check_mark(True, "API authentication dependencies")
        
        from business_intel_scraper.backend.security.auth import AuthManager
        auth = AuthManager()
        token = auth.create_token("test_user")
        token_ok = len(token) > 50  # JWT tokens are long
        all_good &= check_mark(token_ok, f"JWT token generation (length: {len(token)})")
        
    except Exception as e:
        all_good &= check_mark(False, f"Essential API components: {e}")
    
    # Note about advanced components
    print(f"\n💡 Note: Some advanced API modules may show warnings during import.")
    print(f"   This is normal and doesn't affect core scraping functionality.")
    
    # Final Results
    print_header("📊 VALIDATION RESULTS")
    
    if all_good:
        print("🎉 ALL CHECKS PASSED!")
        print("\n✅ Your Business Intelligence Scraper installation is ready!")
        print("\n📋 Next Steps:")
        print("   1. Start the API server: uvicorn business_intel_scraper.backend.api.main:app --port 8000")
        print("   2. Visit the API docs: http://localhost:8000/docs")
        print("   3. Test the CLI: python bis.py --help")
        print("   4. Begin scraping operations!")
    else:
        print("❌ SOME CHECKS FAILED!")
        print("\n🔧 Please review the failed items above and:")
        print("   1. Ensure all requirements are installed: pip install -r requirements.txt")
        print("   2. Verify your .env file configuration")
        print("   3. Check the setup guide: docs/setup.md")
        print("   4. Run this validation script again")
        
        print("\n🆘 If issues persist:")
        print("   • Check the troubleshooting section in docs/setup.md")
        print("   • Verify your Python version (3.11+ required)")
        print("   • Ensure virtual environment is activated")
    
    print(f"\n{'='*60}")
    return all_good

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"❌ Validation script failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
