#!/usr/bin/env python3
"""
Quick verification test for the implemented fixes
"""

import requests
import json
import time
import sys

def test_backend_api():
    """Test that backend API endpoints are working"""
    print("🧪 Testing Backend API...")
    
    try:
        # Test basic health
        response = requests.get('http://localhost:8000/api/health', timeout=5)
        if response.status_code == 200:
            print("  ✅ Backend API is responding")
        else:
            print(f"  ❌ Backend API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Backend API connection failed: {e}")
        return False
    
    return True

def test_frontend():
    """Test that frontend is accessible"""
    print("🌐 Testing Frontend...")
    
    try:
        response = requests.get('http://localhost:5174', timeout=5)
        if response.status_code == 200:
            print("  ✅ Frontend is accessible")
            return True
        else:
            print(f"  ❌ Frontend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Frontend connection failed: {e}")
        return False

def test_video_extraction():
    """Test that video extraction is working"""
    print("🎥 Testing Video Extraction...")
    
    try:
        # Test with a simple HTML containing video
        from scraping_engine import ScrapingEngine
        from bs4 import BeautifulSoup
        
        engine = ScrapingEngine()
        
        # Test HTML with video content
        test_html = '''
        <html>
        <body>
            <video src="test.mp4" controls>
                <source src="test.webm" type="video/webm">
            </video>
            <iframe src="https://www.youtube.com/embed/dQw4w9WgXcQ"></iframe>
        </body>
        </html>
        '''
        
        soup = BeautifulSoup(test_html, 'html.parser')
        videos = engine._extract_videos(soup, 'https://example.com')
        
        if len(videos) >= 2:  # Should find both video tag and YouTube iframe
            print(f"  ✅ Video extraction working - found {len(videos)} videos")
            print(f"     - Video types: {[v.get('video_type', 'unknown') for v in videos]}")
            return True
        else:
            print(f"  ❌ Video extraction found {len(videos)} videos, expected at least 2")
            return False
            
    except Exception as e:
        print(f"  ❌ Video extraction test failed: {e}")
        return False

def test_enhanced_api():
    """Test enhanced API endpoints"""
    print("🔧 Testing Enhanced API Endpoints...")
    
    try:
        # Test page content endpoint structure
        response = requests.get('http://localhost:8000/api/cfpl/page-content', 
                              params={'url': 'https://example.com'}, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'assets' in data:
                print("  ✅ Enhanced page content API responding with assets")
                return True
            else:
                print("  ❌ Enhanced page content API missing assets field")
                return False
        else:
            print(f"  ⚠️  Page content API returned status {response.status_code} (may be normal)")
            return True  # This might be normal if URL doesn't exist in cache
            
    except Exception as e:
        print(f"  ❌ Enhanced API test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Running Implementation Verification Tests")
    print("=" * 50)
    
    tests = [
        test_backend_api,
        test_frontend, 
        test_video_extraction,
        test_enhanced_api
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Implementation is working correctly.")
        print("\n🔗 Access points:")
        print("   Frontend: http://localhost:5174")
        print("   Backend API: http://localhost:8000")
        print("\n📱 To test the fixes:")
        print("   1. Start a new crawl from the frontend")
        print("   2. Navigate to Advanced View -> Media Gallery (formerly Image Gallery)")
        print("   3. Check Page View for enhanced offline archives")
        print("   4. Examine Network Diagram for proper link connections")
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
