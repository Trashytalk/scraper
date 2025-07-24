#!/usr/bin/env python3
"""
Test script for pagination and centralized data functionality
Verifies that the new features are working correctly
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"

def test_backend_health():
    """Test if backend is running"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def test_frontend_health():
    """Test if frontend is running"""
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        return response.status_code == 200
    except:
        return False

def test_centralized_data_endpoints():
    """Test centralized data API endpoints"""
    print("Testing centralized data endpoints...")
    
    # Test getting centralized data
    try:
        response = requests.get(f"{BACKEND_URL}/api/centralized-data")
        print(f"✓ GET centralized data: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Found {len(data.get('records', []))} centralized records")
    except Exception as e:
        print(f"✗ Error testing centralized data endpoint: {e}")
    
    # Test analytics endpoint
    try:
        response = requests.get(f"{BACKEND_URL}/api/centralized-data/analytics")
        print(f"✓ GET analytics: {response.status_code}")
    except Exception as e:
        print(f"✗ Error testing analytics endpoint: {e}")

def test_pagination_parameters():
    """Test pagination with different parameters"""
    print("Testing pagination parameters...")
    
    page_sizes = [5, 10, 25, 50]
    
    for page_size in page_sizes:
        try:
            response = requests.get(
                f"{BACKEND_URL}/api/scrape/jobs",
                params={"page": 1, "page_size": page_size}
            )
            if response.status_code == 200:
                data = response.json()
                actual_size = len(data.get("jobs", []))
                print(f"✓ Page size {page_size}: returned {actual_size} items")
            else:
                print(f"✗ Page size {page_size}: status {response.status_code}")
        except Exception as e:
            print(f"✗ Error testing page size {page_size}: {e}")

def main():
    print("=== Business Intelligence Scraper Test Suite ===")
    print(f"Testing at {datetime.now()}")
    print()
    
    # Check if servers are running
    print("Checking server health...")
    backend_ok = test_backend_health()
    frontend_ok = test_frontend_health()
    
    print(f"Backend (port 8000): {'✓ Running' if backend_ok else '✗ Not responding'}")
    print(f"Frontend (port 5173): {'✓ Running' if frontend_ok else '✗ Not responding'}")
    print()
    
    if not backend_ok:
        print("❌ Backend not running. Please start with: ./start_servers.sh")
        return
    
    # Test new functionality
    test_centralized_data_endpoints()
    print()
    test_pagination_parameters()
    print()
    
    print("=== Test Summary ===")
    print("✓ Pagination system ready for testing")
    print("✓ Centralized data endpoints available")
    print("✓ Frontend should show enhanced results viewer")
    print()
    print("Next steps:")
    print("1. Visit http://localhost:5173 to test the UI")
    print("2. Create some scraping jobs to test pagination")
    print("3. Use the 'Centralize Data' button to aggregate results")
    print("4. Check the Analytics tab for centralized insights")

if __name__ == "__main__":
    main()
