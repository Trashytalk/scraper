#!/usr/bin/env python3
"""
🚀 Quick System Check - Business Intelligence Scraper Platform
================================================================
Simplified validation to confirm system readiness for manual testing.
"""

import json
import time

import requests


def check_backend():
    """Check if backend is healthy"""
    try:
        print("🔧 Checking Backend Health...")
        response = requests.get("http://localhost:8000/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Backend Status: {data.get('status', 'unknown')}")
            print(
                f"   📊 Total Requests: {data.get('system', {}).get('total_requests', 0)}"
            )
            print(f"   🔄 Uptime: {data.get('system', {}).get('uptime_seconds', 0)}s")
            return True
        else:
            print(f"   ❌ Backend Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Backend Error: {e}")
        return False


def check_authentication():
    """Test authentication system"""
    try:
        print("\n🔐 Checking Authentication...")

        # Test valid login
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post(
            "http://localhost:8000/api/auth/login", json=login_data, timeout=10
        )

        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print(
                f"   ✅ Valid Login: Token received ({len(token) if token else 0} chars)"
            )

            # Test API access with token
            headers = {"Authorization": f"Bearer {token}"}
            api_response = requests.get(
                "http://localhost:8000/api/jobs", headers=headers, timeout=10
            )

            if api_response.status_code == 200:
                print(f"   ✅ API Access: Jobs endpoint accessible")
                return True
            else:
                print(f"   ❌ API Access: {api_response.status_code}")
                return False
        else:
            print(f"   ❌ Authentication: {response.status_code}")
            return False

    except Exception as e:
        print(f"   ❌ Authentication Error: {e}")
        return False


def check_database():
    """Check database connectivity"""
    try:
        print("\n💾 Checking Database...")
        import os
        import sqlite3

        db_path = "/home/homebrew/scraper/data.db"
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM crawl_cache")
            count = cursor.fetchone()[0]
            print(f"   ✅ Database: {count} cached entries found")
            conn.close()
            return True
        else:
            print(f"   ❌ Database: File not found at {db_path}")
            return False

    except Exception as e:
        print(f"   ❌ Database Error: {e}")
        return False


def check_enhanced_features():
    """Check if enhanced crawling components are available"""
    try:
        print("\n🎯 Checking Enhanced Features...")

        # Check if scraping engine is available
        try:
            import scraping_engine

            print("   ✅ Scraping Engine: Module available")
            engine_available = True
        except ImportError:
            print("   ❌ Scraping Engine: Module not found")
            engine_available = False

        # Check if settings are configured
        try:
            import settings

            print("   ✅ Settings: Configuration available")
            settings_available = True
        except ImportError:
            print("   ❌ Settings: Configuration not found")
            settings_available = False

        return engine_available and settings_available

    except Exception as e:
        print(f"   ❌ Enhanced Features Error: {e}")
        return False


def main():
    """Run complete system check"""
    print("🧪 Business Intelligence Scraper - Quick System Check")
    print("=" * 60)

    results = []

    # Run all checks
    results.append(("Backend Health", check_backend()))
    results.append(("Authentication", check_authentication()))
    results.append(("Database", check_database()))
    results.append(("Enhanced Features", check_enhanced_features()))

    # Calculate results
    passed = sum(1 for _, result in results if result)
    total = len(results)
    success_rate = (passed / total) * 100

    print("\n" + "=" * 60)
    print("📊 SYSTEM READINESS REPORT")
    print("=" * 60)
    print(f"Total Checks: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {success_rate:.1f}%")

    print("\n📋 Check Details:")
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")

    print("\n🎯 Manual Testing Readiness:")
    if success_rate >= 75:
        print("✅ READY - System is ready for manual testing")
        print("\n📝 Next Steps:")
        print("1. Open http://localhost:5173 in your browser")
        print("2. Login with admin/admin123")
        print("3. Follow MANUAL_TESTING_GUIDE.md for comprehensive testing")
        print("4. Use QUICK_TESTING_CHECKLIST.md for essential tests")
    else:
        print("❌ NOT READY - Fix issues before manual testing")
        print("\n📝 Recommendations:")
        for name, result in results:
            if not result:
                print(f"   - Fix: {name}")

    print("\n🚀 System Status Summary:")
    if success_rate == 100:
        print("   🎉 Perfect! All systems operational")
    elif success_rate >= 75:
        print("   ✅ Good! Most systems working, ready for testing")
    elif success_rate >= 50:
        print("   ⚠️  Partial! Some issues need attention")
    else:
        print("   ❌ Critical! Major issues need resolution")


if __name__ == "__main__":
    main()
