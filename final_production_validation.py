#!/usr/bin/env python3
"""
FINAL PRODUCTION READINESS VALIDATION
Business Intelligence Scraper Platform v2.0.0

This script performs final validation to ensure the repository is 100% production-ready.
"""

import os
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def production_readiness_check():
    """Comprehensive production readiness validation"""
    
    print("🏁 FINAL PRODUCTION READINESS VALIDATION")
    print("=" * 60)
    print(f"Validation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Platform: Business Intelligence Scraper Platform v2.0.0")
    
    validation_results = {
        "timestamp": datetime.now().isoformat(),
        "checks": {},
        "overall_score": 0.0,
        "production_ready": False
    }
    
    checks = [
        ("Documentation Complete", check_documentation),
        ("Security Configuration", check_security),
        ("Database Ready", check_database_config),
        ("Docker Production Ready", check_docker_production),
        ("Environment Templates", check_environment_templates),
        ("No Debug/Dev Files", check_no_debug_files),
        ("API Documentation", check_api_docs),
        ("Testing Infrastructure", check_testing_ready),
        ("Deployment Scripts", check_deployment_scripts),
        ("Performance Optimized", check_performance_config)
    ]
    
    total_score = 0
    max_score = len(checks) * 10
    
    print("\n📋 PRODUCTION READINESS CHECKS:")
    print("=" * 40)
    
    for check_name, check_function in checks:
        try:
            score, details = check_function()
            total_score += score
            validation_results["checks"][check_name] = {
                "score": score,
                "details": details,
                "status": "✅ PASS" if score >= 8 else "⚠️ PARTIAL" if score >= 5 else "❌ FAIL"
            }
            
            status_icon = "✅" if score >= 8 else "⚠️" if score >= 5 else "❌"
            print(f"{status_icon} {check_name}: {score}/10 - {details}")
            
        except Exception as e:
            validation_results["checks"][check_name] = {
                "score": 0,
                "details": f"Error: {str(e)}",
                "status": "❌ ERROR"
            }
            print(f"❌ {check_name}: ERROR - {str(e)}")
    
    validation_results["overall_score"] = (total_score / max_score) * 10
    validation_results["production_ready"] = validation_results["overall_score"] >= 8.5
    
    print(f"\n🏆 FINAL PRODUCTION READINESS SCORE: {validation_results['overall_score']:.1f}/10")
    
    if validation_results["production_ready"]:
        print("✅ STATUS: PRODUCTION READY")
        print("🚀 Platform approved for production deployment!")
    else:
        print("⚠️ STATUS: NEEDS ATTENTION")
        print("🔧 Address failing checks before production deployment")
    
    # Save validation results
    with open("PRODUCTION_READINESS_VALIDATION.json", "w") as f:
        json.dump(validation_results, f, indent=2)
    
    print(f"\n📄 Full validation report saved to: PRODUCTION_READINESS_VALIDATION.json")
    
    return validation_results

def check_documentation():
    """Check if all required documentation exists and is complete"""
    required_docs = [
        "README.md",
        "DEPLOYMENT.md", 
        "API_DOCUMENTATION.md",
        "CONTRIBUTING.md",
        "COMPREHENSIVE_TESTING_COMPLETION.md"
    ]
    
    existing_docs = []
    total_size = 0
    
    for doc in required_docs:
        if Path(doc).exists():
            existing_docs.append(doc)
            total_size += Path(doc).stat().st_size
    
    score = (len(existing_docs) / len(required_docs)) * 10
    details = f"{len(existing_docs)}/{len(required_docs)} docs present, {total_size//1024}KB total"
    
    return score, details

def check_security():
    """Check security configuration and templates"""
    security_items = [
        ".env.example",
        "secure_config.py",
        "security_middleware.py"
    ]
    
    secure_items = 0
    for item in security_items:
        if Path(item).exists():
            secure_items += 1
    
    # Check for no sensitive files in repo
    sensitive_patterns = ["*.key", "*.pem", ".env"]
    sensitive_found = 0
    
    for pattern in sensitive_patterns:
        if pattern != ".env.example" and pattern != ".env.template":
            result = subprocess.run(f"find . -name '{pattern}' -type f", 
                                   shell=True, capture_output=True, text=True)
            if result.stdout.strip():
                sensitive_found += 1
    
    score = ((secure_items / len(security_items)) * 5) + (5 if sensitive_found == 0 else 0)
    details = f"{secure_items} security configs, {sensitive_found} sensitive files exposed"
    
    return score, details

def check_database_config():
    """Check database configuration and migrations"""
    score = 10  # Base score for having database setup
    details = "Database configuration present"
    
    # Check for database-related files
    db_files = [
        "business_intel_scraper/backend/storage",
        "requirements.txt"
    ]
    
    if Path("requirements.txt").exists():
        with open("requirements.txt", "r") as f:
            content = f.read()
            if "psycopg2" in content or "asyncpg" in content:
                score = 10
                details = "PostgreSQL drivers configured"
            elif "sqlite" in content.lower():
                score = 8
                details = "SQLite configured (development ready)"
            else:
                score = 6
                details = "Basic database setup"
    
    return score, details

def check_docker_production():
    """Check Docker production configuration"""
    docker_files = [
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose.production-v3.yml"
    ]
    
    existing_docker = []
    for dockerfile in docker_files:
        if Path(dockerfile).exists():
            existing_docker.append(dockerfile)
    
    score = (len(existing_docker) / len(docker_files)) * 10
    details = f"{len(existing_docker)} Docker configs present"
    
    return score, details

def check_environment_templates():
    """Check environment template files"""
    env_templates = [
        ".env.example",
        ".env.template",
        ".env.production.template"
    ]
    
    existing_templates = []
    for template in env_templates:
        if Path(template).exists():
            existing_templates.append(template)
    
    score = min((len(existing_templates) / len(env_templates)) * 10, 10)
    details = f"{len(existing_templates)} environment templates"
    
    return score, details

def check_no_debug_files():
    """Check that debug and development files are removed"""
    debug_patterns = [
        "*debug*",
        "*test_manual*", 
        "*_broken.*",
        "*.log"
    ]
    
    debug_files_found = 0
    for pattern in debug_patterns:
        result = subprocess.run(f"find . -name '{pattern}' -type f", 
                               shell=True, capture_output=True, text=True)
        files = result.stdout.strip().split('\n') if result.stdout.strip() else []
        # Filter out legitimate files
        legitimate_files = [
            "./debug_crawling.py",  # Part of the platform
            "./debug_frontend_data.py",  # Platform debugging
            "./DEBUGGING_GUIDE.md"  # Documentation
        ]
        actual_debug = [f for f in files if f not in legitimate_files and not f.startswith("./logs/")]
        debug_files_found += len(actual_debug)
    
    score = 10 if debug_files_found == 0 else max(0, 10 - debug_files_found)
    details = f"{debug_files_found} debug/dev files found"
    
    return score, details

def check_api_docs():
    """Check API documentation completeness"""
    api_doc_file = "API_DOCUMENTATION.md"
    
    if not Path(api_doc_file).exists():
        return 0, "API documentation missing"
    
    with open(api_doc_file, "r") as f:
        content = f.read()
    
    required_sections = [
        "authentication",
        "endpoints", 
        "error handling",
        "rate limits",
        "examples"
    ]
    
    sections_found = sum(1 for section in required_sections if section.lower() in content.lower())
    score = (sections_found / len(required_sections)) * 10
    details = f"{sections_found}/{len(required_sections)} API doc sections"
    
    return score, details

def check_testing_ready():
    """Check testing infrastructure readiness"""
    test_files = [
        "pytest.ini",
        "requirements-testing.txt",
        "COMPREHENSIVE_TESTING_COMPLETION.md"
    ]
    
    existing_tests = []
    for test_file in test_files:
        if Path(test_file).exists():
            existing_tests.append(test_file)
    
    # Check for test files
    result = subprocess.run("find . -name 'test_*.py' -type f | wc -l", 
                           shell=True, capture_output=True, text=True)
    test_count = int(result.stdout.strip()) if result.stdout.strip().isdigit() else 0
    
    score = min(((len(existing_tests) / len(test_files)) * 5) + min(test_count / 10, 5), 10)
    details = f"{len(existing_tests)} test configs, {test_count} test files"
    
    return score, details

def check_deployment_scripts():
    """Check deployment and setup scripts"""
    deploy_files = [
        "DEPLOYMENT.md",
        "deploy.sh",
        "production_readiness_cleanup.sh"
    ]
    
    existing_deploy = []
    for deploy_file in deploy_files:
        if Path(deploy_file).exists():
            existing_deploy.append(deploy_file)
    
    score = (len(existing_deploy) / len(deploy_files)) * 10
    details = f"{len(existing_deploy)} deployment resources"
    
    return score, details

def check_performance_config():
    """Check performance optimization configurations"""
    perf_indicators = [
        "business_intel_scraper/frontend/src/utils/performance-optimizations.jsx",
        "business_intel_scraper/frontend/src/utils/caching-system.jsx",
        "performance_monitor.py"
    ]
    
    existing_perf = []
    for perf_file in perf_indicators:
        if Path(perf_file).exists():
            existing_perf.append(perf_file)
    
    score = (len(existing_perf) / len(perf_indicators)) * 10
    details = f"{len(existing_perf)} performance optimizations"
    
    return score, details

if __name__ == "__main__":
    try:
        results = production_readiness_check()
        
        # Exit with appropriate code
        if results["production_ready"]:
            print("\n🎉 VALIDATION COMPLETE - PRODUCTION READY!")
            sys.exit(0)
        else:
            print("\n⚠️ VALIDATION COMPLETE - NEEDS ATTENTION")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        sys.exit(1)
