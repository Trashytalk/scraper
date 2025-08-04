#!/usr/bin/env python3
"""
Test script specifically for the new Phase 1-4 AI features
"""

import json

import requests


def test_ai_features():
    """Test the new AI analytics features"""
    base_url = "http://localhost:8000"

    print("🤖 Testing Phase 1-4 AI Features...")

    # Login to get token
    try:
        login_data = {"username": "admin", "password": "admin123"}

        print("\n🔐 Logging in...")
        login_response = requests.post(f"{base_url}/api/auth/login", json=login_data)

        if login_response.status_code == 200:
            token_data = login_response.json()
            token = token_data.get("access_token")
            print(f"✅ Login successful")

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Login failed: {e}")
        return False

    # Test AI Service Status
    try:
        print("\n🔋 Testing AI Service Status...")
        response = requests.get(f"{base_url}/api/ai/service/status", headers=headers)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            status = response.json()
            print(
                f"   AI Service Available: {status.get('ai_service_available', False)}"
            )
            if status.get("capabilities"):
                caps = status["capabilities"]
                print(f"   Content Clustering: {caps.get('content_clustering', False)}")
                print(
                    f"   Predictive Analytics: {caps.get('predictive_analytics', False)}"
                )
                print(
                    f"   Real-time Monitoring: {caps.get('real_time_monitoring', False)}"
                )
                print("✅ AI Service Status working!")
        else:
            print(f"❌ AI Service Status failed: {response.status_code}")
            print(f"   Response: {response.text}")

    except Exception as e:
        print(f"❌ AI Service Status error: {e}")

    # Test AI Realtime Dashboard
    try:
        print("\n📊 Testing AI Realtime Dashboard...")
        response = requests.get(
            f"{base_url}/api/ai/realtime-dashboard", headers=headers
        )
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            dashboard = response.json()
            print(f"   Dashboard data available: {bool(dashboard)}")
            if dashboard.get("ai_service_stats"):
                stats = dashboard["ai_service_stats"]
                print(f"   Analyses completed: {stats.get('analyses_completed', 0)}")
                print(
                    f"   Avg processing time: {stats.get('avg_processing_time', 0):.2f}s"
                )
            print("✅ AI Dashboard working!")
        else:
            print(f"❌ AI Dashboard failed: {response.status_code}")
            print(f"   Response: {response.text}")

    except Exception as e:
        print(f"❌ AI Dashboard error: {e}")

    # Test AI Analysis with sample data
    try:
        print("\n🧠 Testing AI Analysis...")
        sample_data = [
            {
                "title": "Sample Article 1",
                "content": "This is test content about technology and AI",
                "url": "https://example.com/1",
            },
            {
                "title": "Sample Article 2",
                "content": "Another article about machine learning and data science",
                "url": "https://example.com/2",
            },
            {
                "title": "Sample Article 3",
                "content": "Content about web scraping and automation tools",
                "url": "https://example.com/3",
            },
        ]

        analysis_request = {
            "data": sample_data,
            "analysis_type": "full",
            "options": {"include_visualizations": True},
        }

        response = requests.post(
            f"{base_url}/api/ai/analyze", json=analysis_request, headers=headers
        )
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"   Analysis ID: {result.get('analysis_id', 'N/A')}")
            print(f"   Processing time: {result.get('processing_time', 'N/A')}s")
            print(f"   Recommendations: {len(result.get('recommendations', []))}")
            print(f"   Insights available: {bool(result.get('insights'))}")
            print("✅ AI Analysis working!")
        else:
            print(f"❌ AI Analysis failed: {response.status_code}")
            print(f"   Response: {response.text}")

    except Exception as e:
        print(f"❌ AI Analysis error: {e}")

    # Test AI Recommendations
    try:
        print("\n💡 Testing AI Recommendations...")
        response = requests.get(f"{base_url}/api/ai/recommendations", headers=headers)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            recommendations = response.json()
            print(
                f"   Recommendations available: {len(recommendations.get('recommendations', []))}"
            )
            print("✅ AI Recommendations working!")
        else:
            print(f"❌ AI Recommendations failed: {response.status_code}")
            print(f"   Response: {response.text}")

    except Exception as e:
        print(f"❌ AI Recommendations error: {e}")

    print("\n🎯 Phase 1-4 AI Features Test Complete!")
    print("\n💡 Next steps:")
    print("   1. Open http://localhost:5173 in your browser")
    print("   2. Login with admin/admin123")
    print("   3. Click on the '🤖 AI Analytics' tab")
    print("   4. Test the new AI features in the GUI")
    print("   5. Create a job and use 'AI Analysis Tools'")

    return True


if __name__ == "__main__":
    test_ai_features()
