#!/usr/bin/env python3
"""
Automated Modal Testing Script
Tests the backend API and creates test data for frontend modal testing
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_backend_connection():
    """Test if backend is responding"""
    print("� Testing backend connection...")
    try:
        # Try the API docs endpoint which should always be available
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ Backend is responding")
            return True
        else:
            # Try the root endpoint
            response = requests.get(f"{BASE_URL}/")
            if response.status_code == 200:
                print("✅ Backend is responding")
                return True
            else:
                print(f"❌ Backend responded with status: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False

def create_test_user():
    """Use the default admin user for testing"""
    print("👤 Using default admin user...")
    try:
        # Login with default admin credentials
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("✅ Login successful, token obtained")
            return token
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return None

def create_test_job(token):
    """Create a test job for modal testing"""
    print("📝 Creating test job...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        job_data = {
            "name": "BBC Business Test Job",
            "url": "https://www.bbc.com/business",
            "type": "news_scraper",
            "config": {
                "extract_links": True,
                "max_pages": 3,
                "extract_content": True
            }
        }
        
        response = requests.post(f"{BASE_URL}/api/jobs", json=job_data, headers=headers)
        
        if response.status_code in [200, 201]:
            job = response.json()
            job_id = job.get("id")
            if job_id:
                print(f"✅ Test job created with ID: {job_id}")
                return job_id
            else:
                print(f"⚠️ Job created but no ID returned: {job}")
                return None
        else:
            print(f"❌ Job creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Job creation failed: {e}")
        return None

def start_and_complete_job(token, job_id):
    """Start the job and wait for completion"""
    print(f"▶️ Starting job {job_id}...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Start the job
        response = requests.post(f"{BASE_URL}/api/jobs/{job_id}/start", headers=headers)
        if response.status_code == 200:
            print("✅ Job started successfully")
        else:
            print(f"⚠️ Job start response: {response.status_code}")
        
        # Wait for completion (max 30 seconds)
        print("⏳ Waiting for job completion...")
        for i in range(30):
            response = requests.get(f"{BASE_URL}/api/jobs/{job_id}", headers=headers)
            if response.status_code == 200:
                job = response.json()
                status = job.get("status", "unknown")
                print(f"Status check {i+1}: {status}")
                
                if status == "completed":
                    print("✅ Job completed successfully!")
                    return True
                elif status == "failed":
                    print("❌ Job failed")
                    return False
                elif status == "running":
                    time.sleep(2)
                    continue
            else:
                print(f"❌ Status check failed: {response.status_code}")
                return False
        
        print("⏰ Job completion timeout")
        return False
        
    except Exception as e:
        print(f"❌ Job execution failed: {e}")
        return False

def test_job_details_api(token, job_id):
    """Test the job details API endpoint"""
    print(f"🔍 Testing job details API for job {job_id}...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/jobs/{job_id}", headers=headers)
        
        if response.status_code == 200:
            job_details = response.json()
            print("✅ Job details API working")
            print(f"Job details keys: {list(job_details.keys())}")
            return job_details
        else:
            print(f"❌ Job details API failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Job details API error: {e}")
        return None

def test_job_results_api(token, job_id):
    """Test the job results API endpoint"""
    print(f"📊 Testing job results API for job {job_id}...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/jobs/{job_id}/results", headers=headers)
        
        if response.status_code == 200:
            results = response.json()
            print("✅ Job results API working")
            print(f"Results structure: {type(results)}")
            if isinstance(results, dict):
                print(f"Results keys: {list(results.keys())}")
            elif isinstance(results, list):
                print(f"Results count: {len(results)}")
                if len(results) > 0:
                    print(f"Sample result keys: {list(results[0].keys()) if isinstance(results[0], dict) else 'Not a dict'}")
            return results
        else:
            print(f"❌ Job results API failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Job results API error: {e}")
        return None

def generate_browser_test_script(job_id):
    """Generate JavaScript code for browser testing"""
    print("🌐 Generating browser test script...")
    
    browser_script = f"""
// === AUTOMATED MODAL TEST SCRIPT ===
console.log('🧪 Starting automated modal tests...');

// Test Configuration
const TEST_JOB_ID = {job_id};

// Simple debugging setup
document.addEventListener('click', (event) => {{
  if (event.target.tagName === 'BUTTON') {{
    const buttonText = event.target.textContent.trim();
    console.log(`🖱️ Button clicked: "${{buttonText}}"`);
    
    if (buttonText.includes('Details') || buttonText.includes('View Results')) {{
      console.log('🎯 MODAL TRIGGER BUTTON CLICKED!');
      
      setTimeout(() => {{
        const modals = document.querySelectorAll('div[style*="position: fixed"]');
        console.log(`📊 Modals found: ${{modals.length}}`);
        if (modals.length === 0) {{
          console.log('❌ NO MODAL APPEARED!');
        }} else {{
          console.log('✅ Modal appeared successfully!');
          console.log('Modal element:', modals[0]);
        }}
      }}, 500);
    }}
  }}
}});

// API call monitoring
const origFetch = window.fetch;
window.fetch = function(...args) {{
  const url = args[0];
  console.log(`🌐 API Call: ${{url}}`);
  
  return origFetch.apply(this, arguments)
    .then(response => {{
      console.log(`📥 API Response: ${{response.status}} for ${{url}}`);
      return response;
    }})
    .catch(error => {{
      console.log(`❌ API Error: ${{error}}`);
      throw error;
    }});
}};

// Test functions
window.testDetailsButton = () => {{
  console.log('🔍 Testing Details button...');
  const detailsButtons = Array.from(document.querySelectorAll('button')).filter(btn => 
    btn.textContent.includes('Details')
  );
  
  if (detailsButtons.length > 0) {{
    console.log(`Found ${{detailsButtons.length}} Details buttons`);
    detailsButtons[0].click();
  }} else {{
    console.log('❌ No Details buttons found');
  }}
}};

window.testResultsButton = () => {{
  console.log('📊 Testing View Results button...');
  const resultsButtons = Array.from(document.querySelectorAll('button')).filter(btn => 
    btn.textContent.includes('View Results')
  );
  
  if (resultsButtons.length > 0) {{
    console.log(`Found ${{resultsButtons.length}} View Results buttons`);
    resultsButtons[0].click();
  }} else {{
    console.log('❌ No View Results buttons found');
  }}
}};

window.checkModalState = () => {{
  const modals = document.querySelectorAll('div[style*="position: fixed"]');
  console.log(`Current modals: ${{modals.length}}`);
  return modals;
}};

window.runFullTest = () => {{
  console.log('🚀 Running full modal test sequence...');
  
  // Test 1: Check current state
  console.log('Step 1: Checking current state...');
  checkModalState();
  
  // Test 2: Test Details button
  setTimeout(() => {{
    console.log('Step 2: Testing Details button...');
    testDetailsButton();
    
    // Test 3: Test Results button (after Details test)
    setTimeout(() => {{
      console.log('Step 3: Testing Results button...');
      testResultsButton();
      
      setTimeout(() => {{
        console.log('🏁 Test sequence complete!');
        console.log('Final modal state:');
        checkModalState();
      }}, 2000);
    }}, 3000);
  }}, 1000);
}};

console.log('✅ Browser testing ready!');
console.log('Commands available:');
console.log('- testDetailsButton() - Test Details modal');
console.log('- testResultsButton() - Test Results modal');
console.log('- checkModalState() - Check for existing modals');
console.log('- runFullTest() - Run complete test sequence');
console.log('');
console.log('🎯 Test job ID: {job_id}');
console.log('💡 After logging in with admin/admin123, run: runFullTest()');
"""
    
    return browser_script

def main():
    """Run the complete test suite"""
    print("🧪 Starting Backend Modal Testing Suite")
    print("=" * 50)
    
    # Test 1: Backend Connection
    if not test_backend_connection():
        print("❌ Backend connection failed. Please start the backend server.")
        return
    
    # Test 2: User Creation and Authentication
    token = create_test_user()
    if not token:
        print("❌ Authentication failed. Cannot proceed with tests.")
        return
    
    # Test 3: Job Creation
    job_id = create_test_job(token)
    if not job_id:
        print("❌ Job creation failed. Cannot proceed with modal tests.")
        return
    
    # Test 4: Job Execution
    if not start_and_complete_job(token, job_id):
        print("⚠️ Job didn't complete, but proceeding with API tests...")
    
    # Test 5: API Endpoint Testing
    print("\n🔍 Testing API Endpoints")
    print("-" * 30)
    
    job_details = test_job_details_api(token, job_id)
    job_results = test_job_results_api(token, job_id)
    
    # Test 6: Generate Browser Test Script
    print("\n🌐 Browser Testing Preparation")
    print("-" * 30)
    
    browser_script = generate_browser_test_script(job_id)
    
    # Save browser script to file
    with open('/home/homebrew/scraper/browser_test_script.js', 'w') as f:
        f.write(browser_script)
    
    print("✅ Browser test script saved to: browser_test_script.js")
    
    # Summary
    print("\n📋 TEST SUMMARY")
    print("=" * 50)
    print(f"✅ Backend Connection: Working")
    print(f"✅ Authentication: Working (Token obtained)")
    print(f"✅ Job Creation: Working (Job ID: {job_id})")
    print(f"✅ Job Details API: {'Working' if job_details else 'Failed'}")
    print(f"✅ Job Results API: {'Working' if job_results else 'Failed'}")
    print(f"✅ Browser Test Script: Generated")
    
    print("\n🎯 NEXT STEPS:")
    print("1. Open http://localhost:5173 in browser")
    print("2. Login with: admin / admin123")
    print("3. Copy browser_test_script.js content into console")
    print("4. Run: runFullTest()")
    print("5. Observe console output for modal behavior")

if __name__ == "__main__":
    main()
