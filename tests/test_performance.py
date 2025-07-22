#!/usr/bin/env python3
"""
Performance optimization test script.
"""

import asyncio
import time
from business_intel_scraper.backend.performance.optimizer import get_performance_optimizer


async def test_performance_system():
    """Test the performance optimization system."""
    print("🚀 Testing Performance Optimization System")
    print("=" * 50)
    
    try:
        # Initialize optimizer
        optimizer = get_performance_optimizer()
        print("✅ Performance optimizer initialized")
        
        # Test cache operations
        print("\n📋 Testing cache operations...")
        
        # Set some test data
        for i in range(10):
            await optimizer.cache.set(f"test_key_{i}", f"test_value_{i}", ttl=60)
        print("   ✅ Cache write operations completed")
        
        # Read test data
        hits = 0
        for i in range(10):
            result = await optimizer.cache.get(f"test_key_{i}")
            if result is not None:
                hits += 1
        
        print(f"   ✅ Cache hit rate: {hits}/10 ({hits/10:.0%})")
        
        # Test task processing
        print("\n🔄 Testing task processing...")
        
        async def dummy_task(x):
            await asyncio.sleep(0.01)  # 10ms task
            return x * 2
        
        tasks = []
        start_time = time.time()
        
        for i in range(5):
            task = optimizer.task_optimizer.submit_task(
                dummy_task, i, task_name=f"test_task_{i}"
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        task_time = time.time() - start_time
        
        print(f"   ✅ Processed {len(results)} tasks in {task_time:.3f}s")
        print(f"   ✅ Results: {results}")
        
        # Test performance analysis
        print("\n📊 Running performance analysis...")
        analysis = await optimizer.run_performance_analysis()
        
        print("   ✅ Performance analysis completed:")
        cache_stats = analysis.get('cache_performance', {})
        if cache_stats:
            print(f"      Cache hit rate: {cache_stats.get('hit_rate', 0):.1%}")
            print(f"      Total requests: {cache_stats.get('total_requests', 0)}")
        
        system_stats = analysis.get('system_performance', {})
        if system_stats:
            print(f"      CPU usage: {system_stats.get('cpu_percent', 0):.1f}%")
            print(f"      Memory usage: {system_stats.get('memory_percent', 0):.1f}%")
        
        # Test optimization profiles
        print("\n⚙️ Testing optimization profiles...")
        result = await optimizer.apply_optimizations('balanced')
        print(f"   ✅ Applied {result.get('profile_applied', 'balanced')} profile")
        
        if result.get('changes'):
            print("   Changes made:")
            for change in result['changes']:
                print(f"      • {change}")
        
        print("\n✅ All performance tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False
    
    return True


async def test_memory_optimization():
    """Test memory optimization features."""
    print("\n💾 Testing memory optimization...")
    
    try:
        optimizer = get_performance_optimizer()
        
        # Create some test objects
        test_objects = []
        for i in range(100):
            test_objects.append([i] * 100)  # Create some memory usage
        
        # Run memory cleanup
        optimizer.memory_optimizer.cleanup()
        print("   ✅ Memory cleanup completed")
        
        # Get memory stats
        stats = optimizer.memory_optimizer.get_memory_stats()
        print(f"   Current memory usage: {stats.get('current_memory_percent', 0):.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory optimization test failed: {e}")
        return False


def main():
    """Run all performance tests."""
    print("🧪 Performance Optimization Test Suite")
    print("=" * 60)
    
    try:
        # Test basic performance system
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        success1 = loop.run_until_complete(test_performance_system())
        success2 = loop.run_until_complete(test_memory_optimization())
        
        loop.close()
        
        if success1 and success2:
            print("\n🎉 All performance tests passed!")
            print("\n💡 Next steps:")
            print("   • Start the API server: uvicorn backend.api.main:app --reload")
            print("   • Test performance endpoints: curl http://localhost:8000/performance/status")
            print("   • Run CLI commands: python -m business_intel_scraper.cli.performance status")
            return 0
        else:
            print("\n❌ Some tests failed")
            return 1
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Install performance dependencies: pip install -e .[performance]")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
