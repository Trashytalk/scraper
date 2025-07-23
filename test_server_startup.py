#!/usr/bin/env python3
"""
Quick test to verify the FastAPI server can start without errors
"""

import sys
import subprocess
import time
import requests
import signal
from pathlib import Path

def test_server_startup():
    """Test that the FastAPI server can start without errors"""
    
    print("🧪 Testing FastAPI Server Startup")
    print("=" * 40)
    
    # Start the server process
    try:
        print("Starting server...")
        process = subprocess.Popen(
            ["uvicorn", "business_intel_scraper.backend.api.main:app", "--port", "8001"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a few seconds for startup
        time.sleep(5)
        
        # Check if process is still running (not crashed)
        if process.poll() is None:
            print("✅ Server started successfully!")
            
            # Try a simple request
            try:
                response = requests.get("http://localhost:8001/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Health endpoint responding!")
                else:
                    print(f"⚠️  Health endpoint returned status: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"⚠️  Health check failed: {e}")
            
            # Kill the server
            process.terminate()
            process.wait(timeout=5)
            print("✅ Server stopped cleanly")
            return True
            
        else:
            # Process crashed, get error output
            stdout, stderr = process.communicate()
            print("❌ Server failed to start!")
            print("STDERR:", stderr)
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_server_startup()
    if success:
        print("\n🎉 FastAPI server test PASSED!")
        print("You can now start your server with:")
        print("uvicorn business_intel_scraper.backend.api.main:app --reload --port 8000")
    else:
        print("\n❌ FastAPI server test FAILED!")
        print("Please check the error messages above.")
    
    sys.exit(0 if success else 1)
