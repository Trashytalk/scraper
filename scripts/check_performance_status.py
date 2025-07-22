#!/usr/bin/env python3
"""
Performance optimization system status checker.
"""

import sys
import importlib


def check_imports():
    """Check if all performance components can be imported."""
    components = {
        'Performance Optimizer': 'business_intel_scraper.backend.performance.optimizer',
        'Performance Cache': 'business_intel_scraper.backend.performance.optimizer',
        'Performance CLI': 'business_intel_scraper.cli.performance',
        'Performance API': 'business_intel_scraper.backend.api.performance',
        'Analytics Integration': 'business_intel_scraper.backend.performance',
    }
    
    results = {}
    for name, module_path in components.items():
        try:
            importlib.import_module(module_path)
            results[name] = "✅ Available"
        except ImportError as e:
            results[name] = f"❌ Import Error: {e}"
        except Exception as e:
            results[name] = f"⚠️ Error: {e}"
    
    return results


def check_optional_dependencies():
    """Check optional dependencies for enhanced performance."""
    optional_deps = {
        'Redis': 'redis',
        'psutil': 'psutil', 
        'Memory Profiler': 'memory_profiler',
        'Click': 'click',
        'httpx': 'httpx',
    }
    
    results = {}
    for name, module_path in optional_deps.items():
        try:
            importlib.import_module(module_path)
            results[name] = "✅ Available"
        except ImportError:
            results[name] = "❌ Not installed"
        except Exception as e:
            results[name] = f"⚠️ Error: {e}"
    
    return results


def check_performance_system():
    """Check if the performance system can be initialized."""
    try:
        from business_intel_scraper.backend.performance.optimizer import get_performance_optimizer
        optimizer = get_performance_optimizer()
        return "✅ Performance system initialized successfully"
    except ImportError as e:
        return f"❌ Import error: {e}"
    except Exception as e:
        return f"⚠️ Initialization error: {e}"


def main():
    """Run all checks and display results."""
    print("🔍 Performance Optimization System Status Check")
    print("=" * 60)
    
    # Check component imports
    print("\n📦 Component Status:")
    print("-" * 30)
    import_results = check_imports()
    for component, status in import_results.items():
        print(f"{component:<25}: {status}")
    
    # Check optional dependencies
    print("\n🔧 Optional Dependencies:")
    print("-" * 30)
    dep_results = check_optional_dependencies()
    for dep, status in dep_results.items():
        print(f"{dep:<25}: {status}")
    
    # Check system initialization
    print("\n⚡ System Initialization:")
    print("-" * 30)
    system_status = check_performance_system()
    print(f"Performance System      : {system_status}")
    
    # Summary
    print("\n📊 Summary:")
    print("-" * 20)
    
    total_components = len(import_results)
    working_components = sum(1 for status in import_results.values() if "✅" in status)
    
    total_deps = len(dep_results)
    available_deps = sum(1 for status in dep_results.values() if "✅" in status)
    
    print(f"Components: {working_components}/{total_components} working")
    print(f"Dependencies: {available_deps}/{total_deps} available")
    
    if "✅" in system_status:
        print("🎉 Performance system is ready!")
    else:
        print("⚠️ Performance system needs attention")
    
    print("\n💡 Next Steps:")
    if available_deps < total_deps:
        print("   • Install optional dependencies: pip install -e .[performance]")
    if "✅" in system_status:
        print("   • Test the system: python test_performance.py")
        print("   • Run CLI commands: bi-performance status")
        print("   • Start API server: uvicorn backend.api.main:app --reload")
    
    return 0 if "✅" in system_status else 1


if __name__ == "__main__":
    sys.exit(main())
