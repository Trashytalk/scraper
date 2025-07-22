#!/usr/bin/env python3
"""
Quick Error Testing - Essential components only
"""

import sys
import importlib
import traceback

def test_critical_imports():
    """Test only the most critical imports"""
    critical_imports = [
        ("FastAPI", "fastapi", "FastAPI"),
        ("SQLAlchemy", "sqlalchemy", "create_engine"), 
        ("OpenAI", "openai", "OpenAI"),
        ("Requests", "requests", "get"),
        ("Pandas", "pandas", "DataFrame"),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, module_name, attr_name in critical_imports:
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, attr_name):
                print(f"✅ {test_name}")
                passed += 1
            else:
                print(f"⚠️  {test_name}: Missing {attr_name}")
        except ImportError as e:
            print(f"❌ {test_name}: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test_name}: Unexpected error - {e}")
            failed += 1
    
    return passed, failed

def test_our_components():
    """Test our own component imports"""
    our_components = [
        ("Database Config", "business_intel_scraper.database.config", "get_async_session"),
        ("Auth Manager", "business_intel_scraper.backend.security.auth", "AuthManager"),
        ("Rate Limiter", "business_intel_scraper.backend.security.rate_limit", "RateLimiter"),
        ("Playwright Utils", "business_intel_scraper.backend.browser.playwright_utils", "PlaywrightManager"),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, module_name, attr_name in our_components:
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, attr_name):
                print(f"✅ {test_name}")
                passed += 1
            else:
                print(f"❌ {test_name}: Missing {attr_name}")
                failed += 1
        except ImportError as e:
            print(f"❌ {test_name}: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test_name}: {type(e).__name__} - {str(e)[:100]}")
            failed += 1
    
    return passed, failed

def main():
    print("🔍 Quick Error Testing - Essential Components")
    print("=" * 50)
    
    print("\n📦 Testing Critical Dependencies:")
    deps_passed, deps_failed = test_critical_imports()
    
    print("\n🏗️  Testing Our Components:")
    comp_passed, comp_failed = test_our_components()
    
    total_passed = deps_passed + comp_passed
    total_failed = deps_failed + comp_failed
    
    print(f"\n📊 Results: {total_passed} passed, {total_failed} failed")
    
    if total_failed == 0:
        print("🎉 All essential components are working!")
        return True
    else:
        print(f"⚠️  {total_failed} issues found - review before implementation")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
