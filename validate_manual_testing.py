#!/usr/bin/env python3
"""
Automated Manual Testing Validation Script
==========================================
This script helps validate that all manual testing steps work correctly
by automating the checks and providing detailed feedback.
"""

import requests
import time
import sqlite3
import json
import sys
from datetime import datetime

class TestValidator:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:5173"
        self.token = None
        self.test_results = []
        
    def log_test(self, test_name, passed, details=""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def test_system_startup(self):
        """Test 1: System Startup Validation"""
        print("\n🚀 Testing System Startup...")
        
        # Test backend health
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)
            self.log_test("Backend Health Check", 
                         response.status_code == 200,
                         f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Backend Health Check", False, f"Error: {e}")
        
        # Test frontend access
        try:
            response = requests.get(self.frontend_url, timeout=10)
            self.log_test("Frontend Access", 
                         response.status_code == 200,
                         f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Frontend Access", False, f"Error: {e}")
    
    def test_authentication(self):
        """Test 2: Authentication System"""
        print("\n🔐 Testing Authentication...")
        
        # Test valid login
        try:
            login_data = {"username": "admin", "password": "admin123"}
            response = requests.post(f"{self.base_url}/api/auth/login", 
                                   json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.log_test("Valid Login", True, "Token received")
            else:
                self.log_test("Valid Login", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Valid Login", False, f"Error: {e}")
        
        # Test invalid login
        try:
            login_data = {"username": "wrong", "password": "wrong"}
            response = requests.post(f"{self.base_url}/api/auth/login", 
                                   json=login_data, timeout=10)
            self.log_test("Invalid Login Rejection", 
                         response.status_code == 401,
                         f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Invalid Login Rejection", False, f"Error: {e}")
    
    def test_api_endpoints(self):
        """Test 3: API Endpoints"""
        print("\n🔧 Testing API Endpoints...")
        
        if not self.token:
            self.log_test("API Tests", False, "No authentication token available")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Test jobs endpoint
        try:
            response = requests.get(f"{self.base_url}/api/jobs", 
                                  headers=headers, timeout=10)
            self.log_test("Jobs API", 
                         response.status_code == 200,
                         f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Jobs API", False, f"Error: {e}")
        
        # Test analytics endpoint
        try:
            response = requests.get(f"{self.base_url}/api/analytics/dashboard", 
                                  headers=headers, timeout=10)
            self.log_test("Analytics API", 
                         response.status_code == 200,
                         f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Analytics API", False, f"Error: {e}")
        
        # Test performance endpoint
        try:
            response = requests.get(f"{self.base_url}/api/performance/summary", 
                                  headers=headers, timeout=10)
            self.log_test("Performance API", 
                         response.status_code == 200,
                         f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Performance API", False, f"Error: {e}")
    
    def test_job_creation(self):
        """Test 4: Job Creation"""
        print("\n🎯 Testing Job Creation...")
        
        if not self.token:
            self.log_test("Job Creation", False, "No authentication token available")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # Create test job
        job_data = {
            "name": "Automated Test Job",
            "type": "intelligent_crawling",
            "url": "https://example.com",
            "scraper_type": "intelligent",
            "config": {
                "max_depth": 2,
                "max_pages": 5,
                "extract_full_html": True,
                "include_images": True,
                "save_to_database": True
            }
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/jobs", 
                                   json=job_data, headers=headers, timeout=10)
            self.log_test("Job Creation", 
                         response.status_code == 200,
                         f"Status: {response.status_code}")
            
            if response.status_code == 200:
                job = response.json()
                self.test_job_id = job.get("id")
        except Exception as e:
            self.log_test("Job Creation", False, f"Error: {e}")
    
    def test_database_connectivity(self):
        """Test 5: Database Connectivity"""
        print("\n💾 Testing Database...")
        
        try:
            # Check if database file exists
            import os
            db_path = "/home/homebrew/scraper/data.db"
            
            if not os.path.exists(db_path):
                self.log_test("Database File", False, f"Database file not found: {db_path}")
                return
            
            # Test database connection
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check crawl_cache table
            cursor.execute("SELECT COUNT(*) FROM crawl_cache")
            cache_count = cursor.fetchone()[0]
            self.log_test("Database Connectivity", True, f"Found {cache_count} cached entries")
            
            # Check for recent entries
            cursor.execute("SELECT COUNT(*) FROM crawl_cache WHERE crawled_at > datetime('now', '-1 hour')")
            recent_count = cursor.fetchone()[0]
            self.log_test("Recent Database Activity", 
                         recent_count > 0,
                         f"Found {recent_count} recent entries")
            
            conn.close()
            
        except Exception as e:
            self.log_test("Database Connectivity", False, f"Error: {e}")
    
    def test_enhanced_crawling_features(self):
        """Test 6: Enhanced Crawling Features"""
        print("\n🚀 Testing Enhanced Crawling...")
        
        try:
            # Run enhanced crawling test
            import subprocess
            result = subprocess.run(
                ["python3", "test_enhanced_crawling.py"], 
                capture_output=True, text=True, timeout=60
            )
            
            success = result.returncode == 0
            if success and ("success" in result.stdout.lower() or "✅" in result.stdout):
                self.log_test("Enhanced Crawling Test", True, "Enhanced crawling features working")
            else:
                self.log_test("Enhanced Crawling Test", False, 
                             f"Return code: {result.returncode}")
                if result.stdout:
                    print(f"    Output preview: {result.stdout[:200]}...")
                
        except subprocess.TimeoutExpired:
            self.log_test("Enhanced Crawling Test", False, "Test timed out")
        except Exception as e:
            self.log_test("Enhanced Crawling Test", False, f"Error: {e}")
    
    def test_data_centralization(self):
        """Test 7: Data Centralization"""
        print("\n🔄 Testing Data Centralization...")
        
        try:
            # Run centralization test
            import subprocess
            result = subprocess.run(
                ["python3", "test_centralize_data.py"], 
                capture_output=True, text=True, timeout=30
            )
            
            success = result.returncode == 0
            if success and "successful" in result.stdout.lower():
                self.log_test("Data Centralization", True, "Centralization working")
            else:
                self.log_test("Data Centralization", False, 
                             f"Return code: {result.returncode}")
                
        except subprocess.TimeoutExpired:
            self.log_test("Data Centralization", False, "Test timed out")
        except Exception as e:
            self.log_test("Data Centralization", False, f"Error: {e}")
    
    def generate_report(self):
        """Generate final test report"""
        print("\n" + "="*60)
        print("📊 MANUAL TESTING VALIDATION REPORT")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        print("\n📋 Test Details:")
        for result in self.test_results:
            status = "✅" if result["passed"] else "❌"
            print(f"{status} {result['test']}")
            if result["details"]:
                print(f"    {result['details']}")
        
        print("\n🎯 Manual Testing Readiness:")
        if success_rate >= 95:
            print("✅ SYSTEM READY - All manual testing steps should work")
        elif success_rate >= 80:
            print("⚠️ MOSTLY READY - Some manual steps may fail")
        else:
            print("❌ NOT READY - Manual testing likely to encounter issues")
        
        print("\n📝 Next Steps:")
        print("1. Review any failed tests above")
        print("2. Fix issues before manual testing")
        print("3. Use QUICK_TESTING_CHECKLIST.md for manual tests")
        print("4. Follow MANUAL_TESTING_GUIDE.md for detailed testing")
        
        return success_rate >= 95

def main():
    """Main test execution"""
    print("🧪 Business Intelligence Scraper - Manual Testing Validator")
    print("=" * 60)
    
    validator = TestValidator()
    
    # Run all tests
    validator.test_system_startup()
    validator.test_authentication()
    validator.test_api_endpoints()
    validator.test_job_creation()
    validator.test_database_connectivity()
    validator.test_enhanced_crawling_features()
    validator.test_data_centralization()
    
    # Generate final report
    ready = validator.generate_report()
    
    # Exit with appropriate code
    sys.exit(0 if ready else 1)

if __name__ == "__main__":
    main()
