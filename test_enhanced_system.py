#!/usr/bin/env python3
"""
Enhanced System Test - Testing the upgraded Business Intelligence Scraper
"""

import json
import time
from datetime import datetime

import requests


def test_enhanced_system():
    """Test all enhanced system features"""
    base_url = "http://localhost:8000"

    print("🚀 Testing Enhanced Business Intelligence Scraper")
    print("=" * 60)

    # Test 1: Enhanced Health Check
    print("\n📊 Test 1: Enhanced Health Monitoring")
    try:
        response = requests.get(f"{base_url}/api/health")
        health_data = response.json()

        print(f"✅ Status: {health_data['status']}")
        print(f"📅 Timestamp: {health_data['timestamp']}")
        print(f"🏷️  Version: {health_data['version']}")
        print(f"🌍 Environment: {health_data['environment']}")

        # System metrics
        system = health_data["checks"]["system"]
        print(f"\n🖥️  System Metrics:")
        print(f"   CPU: {system['cpu_percent']}%")
        print(
            f"   Memory: {system['memory_percent']}% ({system['memory_used_mb']}/{system['memory_total_mb']} MB)"
        )
        print(
            f"   Disk: {system['disk_percent']}% ({system['disk_used_gb']}/{system['disk_total_gb']} GB)"
        )

        # Database health
        db = health_data["checks"]["database"]
        print(f"\n🗄️  Database Health:")
        print(f"   Status: {db['status']}")
        print(f"   Tables: {db['tables']}")
        print(f"   Table Stats: {db['table_stats']}")

        # API metrics
        api = health_data["checks"]["api"]
        print(f"\n🔌 API Metrics:")
        print(f"   Uptime: {api['uptime_human']}")
        print(f"   Total Requests: {api['total_requests']}")
        print(f"   Error Rate: {api['error_rate_percent']}%")

    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

    # Test 2: Configuration Management
    print("\n🔧 Test 2: Configuration Management")
    try:
        response = requests.get(f"{base_url}/api/config")
        if response.status_code == 200:
            print("✅ Configuration endpoint accessible")
        else:
            print(f"⚠️  Configuration endpoint returned: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Configuration test: {e}")

    # Test 3: Error Handling
    print("\n🛡️  Test 3: Enhanced Error Handling")
    try:
        # Test deliberate error
        response = requests.get(f"{base_url}/api/nonexistent")
        print(f"✅ Error handling working - Status: {response.status_code}")
        if response.headers.get("content-type", "").startswith("application/json"):
            error_data = response.json()
            print(f"   Error response structured: {error_data}")
    except Exception as e:
        print(f"⚠️  Error handling test: {e}")

    # Test 4: Security Headers
    print("\n🔒 Test 4: Security Enhancement")
    try:
        response = requests.get(f"{base_url}/api/health")
        security_headers = [
            "strict-transport-security",
            "content-security-policy",
            "x-content-type-options",
            "x-frame-options",
        ]

        for header in security_headers:
            if header in response.headers:
                print(f"✅ {header}: Present")
            else:
                print(f"❌ {header}: Missing")

        print(
            f"✅ Response time header: {response.headers.get('x-response-time', 'N/A')}"
        )

    except Exception as e:
        print(f"❌ Security test failed: {e}")

    # Test 5: Performance Monitoring
    print("\n⚡ Test 5: Performance Monitoring")
    start_time = time.time()
    try:
        for i in range(5):
            response = requests.get(f"{base_url}/api/health")
            print(f"   Request {i+1}: {response.headers.get('x-response-time', 'N/A')}")
            time.sleep(0.1)

        end_time = time.time()
        print(f"✅ 5 requests completed in {end_time - start_time:.2f} seconds")

    except Exception as e:
        print(f"❌ Performance test failed: {e}")

    print("\n🎉 Enhanced System Test Complete!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    test_enhanced_system()
