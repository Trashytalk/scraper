#!/usr/bin/env python3
"""
Real-world infrastructure testing for Enterprise Visual Analytics Platform
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_database_connectivity():
    """Test database connectivity and models"""
    print("🗄️  Testing Database Connectivity...")
    
    try:
        from business_intel_scraper.backend.db.models import Entity, Connection, Event, Location
        from business_intel_scraper.backend.db.utils import get_db_session
        
        # Test database session
        async with get_db_session() as session:
            # Test basic query
            result = await session.execute("SELECT 1 as test")
            test_value = result.scalar()
            assert test_value == 1
            print("   ✅ Database connection successful")
            
        # Test model imports
        print("   ✅ All database models imported successfully")
        print("   ✅ Database connectivity: PASSED")
        return True
        
    except Exception as e:
        print(f"   ❌ Database connectivity failed: {e}")
        return False

async def test_redis_cache():
    """Test Redis cache connectivity"""
    print("🔄 Testing Redis Cache...")
    
    try:
        from business_intel_scraper.backend.utils.performance import CacheManager
        
        cache = CacheManager()
        
        # Test cache operations
        test_key = "test_connection"
        test_value = "cache_working"
        
        await cache.set(test_key, test_value, ttl=60)
        cached_value = await cache.get(test_key)
        
        assert cached_value == test_value
        print("   ✅ Cache write/read operations successful")
        
        # Clean up
        await cache.delete(test_key)
        print("   ✅ Redis cache: PASSED")
        return True
        
    except Exception as e:
        print(f"   ❌ Redis cache failed: {e}")
        print("   ℹ️  Note: Redis may not be running. Start with: docker-compose up redis")
        return False

async def test_security_components():
    """Test security system initialization"""
    print("🔒 Testing Security Components...")
    
    try:
        from business_intel_scraper.backend.utils.security import EncryptionManager, SecurityAuditLogger
        
        # Test encryption manager
        enc = EncryptionManager()
        test_data = "sensitive_business_data"
        
        encrypted = enc.encrypt_text(test_data)
        decrypted = enc.decrypt_text(encrypted)
        
        assert decrypted == test_data
        print("   ✅ Encryption/decryption working")
        
        # Test audit logger
        audit = SecurityAuditLogger()
        await audit.log_security_event("test_initialization", {"status": "passed"})
        print("   ✅ Security audit logging functional")
        
        print("   ✅ Security components: PASSED")
        return True
        
    except Exception as e:
        print(f"   ❌ Security components failed: {e}")
        return False

async def test_nlp_pipeline():
    """Test NLP processing pipeline"""
    print("🧠 Testing NLP Pipeline...")
    
    try:
        from business_intel_scraper.backend.nlp.pipeline import NLPPipeline
        
        nlp = NLPPipeline()
        
        # Test entity extraction
        sample_text = "Apple Inc. is a technology company based in Cupertino, California, led by CEO Tim Cook."
        entities = await nlp.extract_entities(sample_text)
        
        print(f"   ✅ Extracted {len(entities)} entities from sample text")
        print("   ✅ NLP Pipeline: PASSED")
        return True
        
    except Exception as e:
        print(f"   ❌ NLP Pipeline failed: {e}")
        return False

async def test_performance_monitoring():
    """Test performance monitoring system"""
    print("📊 Testing Performance Monitoring...")
    
    try:
        from business_intel_scraper.backend.utils.performance import PerformanceMonitor
        
        monitor = PerformanceMonitor()
        
        # Record test metrics
        await monitor.record_metric("test_response_time", 125.5)
        await monitor.record_metric("test_memory_usage", 67.8)
        
        # Get metrics
        metrics = await monitor.get_metrics()
        print(f"   ✅ Performance monitoring active, {len(metrics)} metrics tracked")
        
        print("   ✅ Performance Monitoring: PASSED")
        return True
        
    except Exception as e:
        print(f"   ❌ Performance Monitoring failed: {e}")
        return False

async def test_compliance_framework():
    """Test GDPR compliance framework"""
    print("⚖️  Testing Compliance Framework...")
    
    try:
        from business_intel_scraper.backend.utils.compliance import GDPRComplianceManager
        
        gdpr = GDPRComplianceManager()
        
        # Test compliance initialization
        print("   ✅ GDPR compliance manager initialized")
        
        # Test data governance
        policies = gdpr.get_data_policies()
        print(f"   ✅ {len(policies)} data governance policies active")
        
        print("   ✅ Compliance Framework: PASSED")
        return True
        
    except Exception as e:
        print(f"   ❌ Compliance Framework failed: {e}")
        return False

async def run_infrastructure_tests():
    """Run all infrastructure tests"""
    print("🚀 Enterprise Visual Analytics Platform - Infrastructure Testing")
    print("=" * 70)
    
    test_results = {}
    
    # Run all tests
    tests = [
        ("Database Connectivity", test_database_connectivity),
        ("Redis Cache", test_redis_cache), 
        ("Security Components", test_security_components),
        ("NLP Pipeline", test_nlp_pipeline),
        ("Performance Monitoring", test_performance_monitoring),
        ("Compliance Framework", test_compliance_framework)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            test_results[test_name] = result
            if result:
                passed_tests += 1
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            test_results[test_name] = False
        
        print()  # Add spacing between tests
    
    # Summary
    print("=" * 70)
    print("📋 INFRASTRUCTURE TESTING SUMMARY")
    print("=" * 70)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<50} {status}")
    
    print(f"\n🎯 Overall Result: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL INFRASTRUCTURE TESTS PASSED! Platform is ready for real-world testing.")
        return True
    else:
        print("⚠️  Some infrastructure components need attention before proceeding.")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_infrastructure_tests())
    sys.exit(0 if success else 1)
