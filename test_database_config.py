#!/usr/bin/env python3
"""
Database Configuration Validation Test
Specifically tests the database config.py file and its functionality
"""

import os
import asyncio
import time
from pathlib import Path

async def test_database_config_thoroughly():
    """Comprehensive test of the database configuration"""
    print("🗄️  Testing Database Configuration Thoroughly...")
    print("=" * 50)
    
    results = {"passed": [], "failed": [], "warnings": []}
    
    # Test 1: Environment variable loading
    print("1️⃣  Testing Environment Variables...")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        db_url = os.getenv("DATABASE_URL")
        
        if db_url:
            print(f"   ✅ DATABASE_URL loaded: {db_url}")
            results["passed"].append("Environment variable loading")
            
            # Check if it's SQLite (recommended for development)
            if db_url.startswith("sqlite"):
                print("   ✅ Using SQLite (good for development)")
                results["passed"].append("SQLite configuration")
            else:
                print("   ⚠️  Using non-SQLite database (ensure it's available)")
                results["warnings"].append("Non-SQLite database configuration")
        else:
            print("   ❌ DATABASE_URL not found in environment")
            results["failed"].append("DATABASE_URL missing")
    except Exception as e:
        print(f"   ❌ Environment loading failed: {e}")
        results["failed"].append(f"Environment loading: {e}")
    
    # Test 2: Database URL parsing and engine creation
    print("\n2️⃣  Testing Database Engine Creation...")
    try:
        from business_intel_scraper.database.config import (
            ASYNC_DATABASE_URL, SYNC_DATABASE_URL, async_engine, sync_engine
        )
        
        print(f"   ✅ Async URL: {ASYNC_DATABASE_URL}")
        print(f"   ✅ Sync URL: {SYNC_DATABASE_URL}")
        
        # Test engine properties
        if hasattr(async_engine, 'pool'):
            pool_size = getattr(async_engine.pool, 'size', 'Unknown')
            print(f"   ✅ Async engine pool size: {pool_size}")
            results["passed"].append("Async engine configuration")
        
        if hasattr(sync_engine, 'pool'):
            pool_size = getattr(sync_engine.pool, 'size', 'Unknown')
            print(f"   ✅ Sync engine pool size: {pool_size}")
            results["passed"].append("Sync engine configuration")
            
    except Exception as e:
        print(f"   ❌ Engine creation failed: {e}")
        results["failed"].append(f"Engine creation: {e}")
    
    # Test 3: Session factory creation
    print("\n3️⃣  Testing Session Factories...")
    try:
        from business_intel_scraper.database.config import AsyncSessionLocal, SessionLocal
        
        # Test async session factory
        if AsyncSessionLocal:
            print("   ✅ Async session factory created")
            results["passed"].append("Async session factory")
        
        # Test sync session factory  
        if SessionLocal:
            print("   ✅ Sync session factory created")
            results["passed"].append("Sync session factory")
            
    except Exception as e:
        print(f"   ❌ Session factory creation failed: {e}")
        results["failed"].append(f"Session factories: {e}")
    
    # Test 4: Context manager functionality
    print("\n4️⃣  Testing Database Session Context Managers...")
    try:
        from business_intel_scraper.database.config import get_async_session, get_sync_session
        
        # Test async context manager
        async with get_async_session() as session:
            if session:
                print("   ✅ Async session context manager working")
                results["passed"].append("Async context manager")
            else:
                print("   ❌ Async session is None")
                results["failed"].append("Async session creation")
        
        # Test sync session generator
        sync_gen = get_sync_session()
        sync_session = next(sync_gen)
        if sync_session:
            print("   ✅ Sync session generator working")
            results["passed"].append("Sync session generator")
            # Cleanup
            try:
                next(sync_gen)  # This should trigger cleanup
            except StopIteration:
                pass
        else:
            print("   ❌ Sync session is None")
            results["failed"].append("Sync session creation")
            
    except Exception as e:
        print(f"   ❌ Session context manager test failed: {e}")
        results["failed"].append(f"Session context managers: {e}")
    
    # Test 5: Database initialization
    print("\n5️⃣  Testing Database Initialization...")
    try:
        from business_intel_scraper.database.config import init_database
        
        start_time = time.time()
        await init_database()
        init_duration = time.time() - start_time
        
        print(f"   ✅ Database initialization completed in {init_duration:.2f}s")
        results["passed"].append(f"Database initialization ({init_duration:.2f}s)")
        
        if init_duration > 5.0:
            print("   ⚠️  Initialization took longer than expected")
            results["warnings"].append("Slow database initialization")
            
    except Exception as e:
        print(f"   ❌ Database initialization failed: {e}")
        results["failed"].append(f"Database initialization: {e}")
    
    # Test 6: Health check functionality
    print("\n6️⃣  Testing Database Health Check...")
    try:
        from business_intel_scraper.database.config import check_database_health
        
        health_result = await check_database_health()
        
        if health_result.get("status") == "healthy":
            print("   ✅ Database health check passed")
            print(f"      Database type: {health_result.get('database', 'unknown')}")
            print(f"      Entities: {health_result.get('entities_count', 0)}")
            print(f"      Connections: {health_result.get('connections_count', 0)}")
            print(f"      Events: {health_result.get('events_count', 0)}")
            results["passed"].append("Database health check")
        else:
            print(f"   ❌ Database health check failed: {health_result.get('error', 'Unknown error')}")
            results["failed"].append("Database health check")
            
    except Exception as e:
        print(f"   ❌ Health check test failed: {e}")
        results["failed"].append(f"Health check: {e}")
    
    # Test 7: Performance characteristics
    print("\n7️⃣  Testing Database Performance...")
    try:
        from business_intel_scraper.database.config import get_async_session
        from sqlalchemy import text
        
        # Test query performance
        query_times = []
        for i in range(5):
            start_time = time.time()
            async with get_async_session() as session:
                await session.execute(text("SELECT 1"))
            query_times.append(time.time() - start_time)
        
        avg_query_time = sum(query_times) / len(query_times)
        print(f"   ✅ Average query time: {avg_query_time:.4f}s")
        
        if avg_query_time < 0.1:  # Less than 100ms
            print("   ✅ Good query performance")
            results["passed"].append(f"Query performance ({avg_query_time:.4f}s)")
        else:
            print("   ⚠️  Slower than expected query performance")
            results["warnings"].append(f"Slow queries ({avg_query_time:.4f}s)")
            
    except Exception as e:
        print(f"   ❌ Performance test failed: {e}")
        results["failed"].append(f"Performance test: {e}")
    
    # Test 8: Database file validation (for SQLite)
    print("\n8️⃣  Testing Database File...")
    try:
        db_url = os.getenv("DATABASE_URL", "")
        if db_url.startswith("sqlite"):
            # Extract database file path
            db_file = db_url.replace("sqlite:///", "")
            db_path = Path(db_file)
            
            if db_path.exists():
                file_size = db_path.stat().st_size
                print(f"   ✅ Database file exists: {db_file} ({file_size} bytes)")
                results["passed"].append("Database file exists")
                
                # Check if file is writable
                if os.access(db_path, os.W_OK):
                    print("   ✅ Database file is writable")
                    results["passed"].append("Database file permissions")
                else:
                    print("   ⚠️  Database file is not writable")
                    results["warnings"].append("Database file permissions")
            else:
                print("   ⚠️  Database file doesn't exist yet (will be created on first use)")
                results["warnings"].append("Database file not yet created")
        else:
            print("   ✅ Using external database (not file-based)")
            results["passed"].append("External database configuration")
            
    except Exception as e:
        print(f"   ❌ Database file test failed: {e}")
        results["failed"].append(f"Database file validation: {e}")
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 DATABASE CONFIGURATION TEST SUMMARY")
    print("=" * 50)
    
    if results["passed"]:
        print(f"\n✅ PASSED ({len(results['passed'])}):")
        for item in results["passed"]:
            print(f"  ✅ {item}")
    
    if results["warnings"]:
        print(f"\n⚠️  WARNINGS ({len(results['warnings'])}):")
        for item in results["warnings"]:
            print(f"  ⚠️  {item}")
    
    if results["failed"]:
        print(f"\n❌ FAILED ({len(results['failed'])}):")
        for item in results["failed"]:
            print(f"  ❌ {item}")
    
    success_rate = len(results["passed"]) / (len(results["passed"]) + len(results["failed"])) * 100
    print(f"\n🎯 Success Rate: {success_rate:.1f}%")
    
    if len(results["failed"]) == 0:
        print("🎉 Database configuration is working perfectly!")
        return True
    else:
        print("⚠️  Database configuration has issues that need attention.")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(test_database_config_thoroughly())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Test interrupted")
        exit(1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
