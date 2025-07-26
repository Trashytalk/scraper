#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

# Add project root to Python path
project_root = "/home/homebrew/scraper"
sys.path.insert(0, project_root)

# Change to project directory
os.chdir(project_root)

# Load environment variables
load_dotenv()

print("=== Environment Check ===")
print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path[:3]}")  # Show first 3 entries
print(f"DATABASE_URL: {repr(os.getenv('DATABASE_URL'))}")

try:
    print("\n=== Database Config Test ===")
    from business_intel_scraper.database.config import (
        ASYNC_DATABASE_URL,
        SYNC_DATABASE_URL,
    )

    print(f"ASYNC_DATABASE_URL: {ASYNC_DATABASE_URL}")
    print(f"SYNC_DATABASE_URL: {SYNC_DATABASE_URL}")

    print("\n=== Database Initialization Test ===")
    from business_intel_scraper.database.config import init_database
    import asyncio

    asyncio.run(init_database())
    print("✅ Database initialization successful!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
