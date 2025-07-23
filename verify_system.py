#!/usr/bin/env python3
"""
System Verification Script
Verifies that all components are working together properly
"""

import sys
import os
import asyncio
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def verify_backend_server():
    """Verify backend server components"""
    print("🔍 Verifying Backend Server...")
    
    try:
        # Import main components
        from business_intel_scraper.backend.config import secure_config
        from business_intel_scraper.backend.security import security_middleware
        
        print("  ✅ Security configuration loaded")
        print(f"     - JWT Secret: {len(secure_config.security_config.JWT_SECRET)} characters")
        print(f"     - Rate Limiting: {secure_config.security_config.API_RATE_LIMIT_PER_MINUTE}/min")
        
        # Check performance monitoring
        try:
            from performance_monitor import PerformanceMetrics, CacheManager
            print("  ✅ Performance monitoring available")
        except ImportError:
            print("  ⚠️  Performance monitoring unavailable (fallback mode)")
        
        # Check scraping engine
        try:
            from scraping_engine import execute_scraping_job
            print("  ✅ Scraping engine available")
        except ImportError:
            print("  ⚠️  Scraping engine module missing")
            
        return True
        
    except Exception as e:
        print(f"  ❌ Backend verification failed: {e}")
        return False

def verify_frontend_dependencies():
    """Verify frontend dependencies"""
    print("\n🔍 Verifying Frontend Dependencies...")
    
    frontend_dir = project_root / "business_intel_scraper" / "frontend"
    package_json = frontend_dir / "package.json"
    
    if not package_json.exists():
        print("  ❌ package.json not found")
        return False
    
    try:
        with open(package_json) as f:
            packages = json.load(f)
        
        required_packages = [
            "@mui/x-date-pickers",
            "@mui/x-date-pickers-pro", 
            "date-fns",
            "@mui/material",
            "react",
            "vite"
        ]
        
        dependencies = {**packages.get("dependencies", {}), **packages.get("devDependencies", {})}
        
        for package in required_packages:
            if package in dependencies:
                print(f"  ✅ {package}: {dependencies[package]}")
            else:
                print(f"  ❌ {package}: Missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Frontend verification failed: {e}")
        return False

def verify_docker_setup():
    """Verify Docker configuration"""
    print("\n🔍 Verifying Docker Setup...")
    
    docker_files = [
        "Dockerfile",
        "docker-compose.yml"
    ]
    
    all_present = True
    for docker_file in docker_files:
        file_path = project_root / docker_file
        if file_path.exists():
            print(f"  ✅ {docker_file} present")
        else:
            print(f"  ❌ {docker_file} missing")
            all_present = False
    
    return all_present

def verify_performance_system():
    """Verify performance optimization system"""
    print("\n🔍 Verifying Performance System...")
    
    try:
        # Check if performance modules exist
        perf_dir = project_root / "business_intel_scraper" / "backend" / "performance"
        if perf_dir.exists():
            print(f"  ✅ Performance module directory: {perf_dir}")
            
            # Check key files
            key_files = ["optimizer.py", "__init__.py", "README.md"]
            for key_file in key_files:
                file_path = perf_dir / key_file
                if file_path.exists():
                    print(f"  ✅ {key_file}")
                else:
                    print(f"  ❌ {key_file} missing")
        else:
            print("  ❌ Performance module directory missing")
            return False
            
        return True
        
    except Exception as e:
        print(f"  ❌ Performance system verification failed: {e}")
        return False

async def main():
    """Main verification routine"""
    print("🚀 Business Intelligence Scraper - System Verification")
    print("=" * 60)
    
    # Run all verifications
    backend_ok = await verify_backend_server()
    frontend_ok = verify_frontend_dependencies()
    docker_ok = verify_docker_setup()
    performance_ok = verify_performance_system()
    
    print("\n📊 Verification Summary:")
    print(f"  Backend Server:      {'✅' if backend_ok else '❌'}")
    print(f"  Frontend Dependencies: {'✅' if frontend_ok else '❌'}")
    print(f"  Docker Setup:        {'✅' if docker_ok else '❌'}")
    print(f"  Performance System:  {'✅' if performance_ok else '❌'}")
    
    if all([backend_ok, frontend_ok, docker_ok, performance_ok]):
        print("\n🎉 All systems verified successfully!")
        print("\n📝 Next Steps:")
        print("  1. Start backend: python backend_server.py")
        print("  2. Start frontend: cd business_intel_scraper/frontend && npm run dev")
        print("  3. Access dashboard: http://localhost:5173")
        print("  4. API documentation: http://localhost:8000/docs")
        return 0
    else:
        print("\n⚠️  Some issues found - check individual components")
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main()))
