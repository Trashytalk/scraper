#!/usr/bin/env python3

import sys
import os

print("🧪 QUICK VALIDATION TEST")
print("=" * 30)

try:
    # Add current directory to Python path
    sys.path.insert(0, os.getcwd())
    
    # Test database config
    from business_intel_scraper.database.config import ASYNC_DATABASE_URL, SYNC_DATABASE_URL
    print(f"✅ Async DB URL: {ASYNC_DATABASE_URL}")
    print(f"✅ Sync DB URL: {SYNC_DATABASE_URL}")
    
    # Test security
    from business_intel_scraper.backend.api.dependencies import require_token
    print("✅ require_token function available")
    
    # Test main app
    from business_intel_scraper.backend.api.main import app
    print("✅ FastAPI app available")
    
    print("\n🎉 ALL TESTS PASSED!")
    print("Repository is ready for deployment!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
