#!/usr/bin/env python3
"""
Advanced Testing Report Generator for Business Intelligence Scraper

This script provides detailed testing analysis and validation of the platform
based on the Professional Assessment Report claims.
"""

import subprocess
import sys
import time
import json
import os
from datetime import datetime
from pathlib import Path
import requests

def test_phase_validation():
    """Validate the Phase 1-4 implementations claimed in the assessment"""
    print("🔬 PHASE IMPLEMENTATION VALIDATION")
    print("=" * 60)
    
    validation_results = {
        "phase1_error_reduction": False,
        "phase2_infrastructure": False,
        "phase3_ml_integration": False,
        "phase4_ai_deployment": False,
        "overall_maturity": 0.0
    }
    
    # Phase 1: Error Reduction Validation
    print("\n📊 Phase 1: Error Reduction Validation")
    try:
        # Check if core modules import without errors
        exec_cmd = 'python -c "import business_intel_scraper; import backend_server; import scraping_engine; print(\'✅ All core modules imported successfully\')"'
        result = subprocess.run(exec_cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and "successfully" in result.stdout:
            print("  ✅ Core module imports: PASSED")
            validation_results["phase1_error_reduction"] = True
        else:
            print(f"  ❌ Core module imports: FAILED - {result.stderr}")
    except Exception as e:
        print(f"  ❌ Phase 1 validation error: {e}")
    
    # Phase 2: Infrastructure Validation
    print("\n🏗️ Phase 2: Infrastructure Validation")
    try:
        # Check for queue management components
        infrastructure_components = [
            "business_intel_scraper/backend/crawling",
            "business_intel_scraper/backend/security",
            "business_intel_scraper/backend/storage"
        ]
        
        components_found = 0
        for component in infrastructure_components:
            if Path(component).exists():
                components_found += 1
                print(f"  ✅ {component}: Found")
            else:
                print(f"  ❌ {component}: Missing")
        
        if components_found >= 2:
            validation_results["phase2_infrastructure"] = True
            print("  ✅ Infrastructure components: SUFFICIENT")
        else:
            print("  ❌ Infrastructure components: INSUFFICIENT")
            
    except Exception as e:
        print(f"  ❌ Phase 2 validation error: {e}")
    
    # Phase 3: ML Integration Validation
    print("\n🤖 Phase 3: ML Integration Validation")
    try:
        # Check for ML-related imports and components
        ml_cmd = 'python -c "try:\n  import sklearn\n  import pandas\n  import numpy\n  print(\'✅ ML dependencies available\')\nexcept ImportError as e:\n  print(f\'❌ ML dependencies missing: {e}\')"'
        result = subprocess.run(ml_cmd, shell=True, capture_output=True, text=True, timeout=20)
        
        if "available" in result.stdout:
            print("  ✅ ML dependencies: AVAILABLE")
            validation_results["phase3_ml_integration"] = True
        else:
            print(f"  ❌ ML dependencies: {result.stdout.strip()}")
            
        # Check for ML components in codebase
        ml_dirs = [
            "business_intel_scraper/backend/ml",
            "ml_pipeline"
        ]
        
        for ml_dir in ml_dirs:
            if Path(ml_dir).exists():
                print(f"  ✅ {ml_dir}: Found")
                validation_results["phase3_ml_integration"] = True
                break
        else:
            print("  ⚠️ ML pipeline directories: Not found in expected locations")
            
    except Exception as e:
        print(f"  ❌ Phase 3 validation error: {e}")
    
    # Phase 4: AI Deployment Validation  
    print("\n🚀 Phase 4: AI Deployment Validation")
    try:
        # Test API endpoints for AI functionality
        base_url = "http://localhost:8000"
        
        # Test AI status endpoint
        try:
            response = requests.get(f"{base_url}/api/ai/status", timeout=5)
            if response.status_code == 200:
                print("  ✅ AI Status endpoint: ACCESSIBLE")
                validation_results["phase4_ai_deployment"] = True
            else:
                print(f"  ⚠️ AI Status endpoint: Status {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("  ⚠️ AI endpoints: Server not accessible (expected if not running)")
        except Exception as e:
            print(f"  ❌ AI endpoint test error: {e}")
            
        # Check for AI-related code components
        ai_indicators = [
            "business_intel_scraper/backend/ai",
            "test_ai_features.py",
            "test_phase4_ai.py"
        ]
        
        ai_components_found = 0
        for ai_comp in ai_indicators:
            if Path(ai_comp).exists():
                ai_components_found += 1
                print(f"  ✅ {ai_comp}: Found")
        
        if ai_components_found >= 1:
            validation_results["phase4_ai_deployment"] = True
            print("  ✅ AI components: PRESENT")
        else:
            print("  ❌ AI components: MISSING")
            
    except Exception as e:
        print(f"  ❌ Phase 4 validation error: {e}")
    
    # Calculate overall maturity score
    phase_scores = [
        validation_results["phase1_error_reduction"],
        validation_results["phase2_infrastructure"], 
        validation_results["phase3_ml_integration"],
        validation_results["phase4_ai_deployment"]
    ]
    
    validation_results["overall_maturity"] = sum(phase_scores) / len(phase_scores) * 10
    
    print(f"\n📈 PHASE VALIDATION SUMMARY")
    print("=" * 40)
    print(f"Phase 1 (Error Reduction): {'✅ PASSED' if validation_results['phase1_error_reduction'] else '❌ FAILED'}")
    print(f"Phase 2 (Infrastructure): {'✅ PASSED' if validation_results['phase2_infrastructure'] else '❌ FAILED'}")
    print(f"Phase 3 (ML Integration): {'✅ PASSED' if validation_results['phase3_ml_integration'] else '❌ FAILED'}")
    print(f"Phase 4 (AI Deployment): {'✅ PASSED' if validation_results['phase4_ai_deployment'] else '❌ FAILED'}")
    print(f"Validated Maturity Score: {validation_results['overall_maturity']:.1f}/10")
    
    return validation_results

def test_api_comprehensive():
    """Comprehensive API testing"""
    print("\n🌐 COMPREHENSIVE API TESTING")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    api_results = {
        "server_accessible": False,
        "authentication_working": False,
        "endpoints_functional": 0,
        "total_endpoints_tested": 0
    }
    
    # Test server accessibility
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code in [200, 404]:  # 404 is OK, means server is running
            api_results["server_accessible"] = True
            print("✅ Server: ACCESSIBLE")
        else:
            print(f"⚠️ Server: Responding with status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Server: NOT ACCESSIBLE")
        return api_results
    except Exception as e:
        print(f"❌ Server test error: {e}")
        return api_results
    
    # Test authentication
    try:
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post(f"{base_url}/api/auth/login", json=login_data, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                api_results["authentication_working"] = True
                print("✅ Authentication: WORKING")
                token = data["access_token"]
            else:
                print("⚠️ Authentication: No token in response")
                token = None
        else:
            print(f"❌ Authentication: Status {response.status_code}")
            token = None
    except Exception as e:
        print(f"❌ Authentication test error: {e}")
        token = None
    
    # Test various endpoints
    endpoints_to_test = [
        ("/docs", "GET", None),
        ("/api/health", "GET", None),
        ("/", "GET", None),
        ("/api/status", "GET", None),
    ]
    
    if token:
        headers = {"Authorization": f"Bearer {token}"}
        authenticated_endpoints = [
            ("/api/users/me", "GET", headers),
            ("/api/dashboard/stats", "GET", headers),
            ("/api/crawl/jobs", "GET", headers),
        ]
        endpoints_to_test.extend(authenticated_endpoints)
    
    print("\n📊 Endpoint Testing:")
    for endpoint, method, headers in endpoints_to_test:
        api_results["total_endpoints_tested"] += 1
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
            else:
                response = requests.post(f"{base_url}{endpoint}", headers=headers, timeout=5)
            
            if response.status_code == 200:
                api_results["endpoints_functional"] += 1
                print(f"  ✅ {endpoint}: OK")
            elif response.status_code == 404:
                print(f"  ⚠️ {endpoint}: Not Found")
            else:
                print(f"  ⚠️ {endpoint}: Status {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ {endpoint}: Error - {e}")
    
    success_rate = api_results["endpoints_functional"] / api_results["total_endpoints_tested"] * 100 if api_results["total_endpoints_tested"] > 0 else 0
    print(f"\n📈 API Test Summary: {api_results['endpoints_functional']}/{api_results['total_endpoints_tested']} endpoints working ({success_rate:.1f}%)")
    
    return api_results

def generate_comprehensive_report():
    """Generate a comprehensive testing report"""
    print("\n" + "="*80)
    print("📋 COMPREHENSIVE TESTING REPORT")
    print("="*80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Platform: Business Intelligence Scraper Platform v2.0.0")
    
    # Run all validations
    phase_results = test_phase_validation()
    api_results = test_api_comprehensive()
    
    # Generate overall assessment
    print("\n🎯 OVERALL PLATFORM ASSESSMENT")
    print("=" * 40)
    
    # Calculate comprehensive score
    scores = {
        "Phase Implementation": phase_results["overall_maturity"],
        "API Functionality": (api_results["endpoints_functional"] / max(api_results["total_endpoints_tested"], 1)) * 10,
        "Server Accessibility": 10 if api_results["server_accessible"] else 0,
        "Authentication": 10 if api_results["authentication_working"] else 0
    }
    
    overall_score = sum(scores.values()) / len(scores)
    
    print("Component Scores:")
    for component, score in scores.items():
        status = "✅" if score >= 7 else "⚠️" if score >= 4 else "❌"
        print(f"  {status} {component}: {score:.1f}/10")
    
    print(f"\n🏆 OVERALL SCORE: {overall_score:.1f}/10")
    
    # Assessment comparison with Professional Assessment Report
    claimed_score = 9.2
    difference = abs(overall_score - claimed_score)
    
    print(f"\n📊 VALIDATION vs CLAIMS:")
    print(f"Professional Assessment Claim: {claimed_score}/10")
    print(f"Automated Testing Result: {overall_score:.1f}/10")
    print(f"Difference: {difference:.1f} points")
    
    if difference <= 1.0:
        print("✅ VALIDATION: Claims are ACCURATE")
    elif difference <= 2.0:
        print("⚠️ VALIDATION: Claims are MOSTLY ACCURATE with minor discrepancies")
    else:
        print("❌ VALIDATION: Claims may be OVERSTATED")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if overall_score >= 8.0:
        print("✅ Platform is ready for production deployment")
        print("🚀 Focus on performance optimization and scaling")
    elif overall_score >= 6.0:
        print("⚠️ Platform is functional but needs improvement")
        print("🔧 Focus on completing missing components")
    else:
        print("❌ Platform needs significant development")
        print("🛠️ Focus on core functionality completion")
    
    return {
        "overall_score": overall_score,
        "phase_results": phase_results,
        "api_results": api_results,
        "scores": scores
    }

if __name__ == "__main__":
    try:
        results = generate_comprehensive_report()
        
        # Save results to file
        with open("testing_validation_report.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📄 Full report saved to: testing_validation_report.json")
        
    except Exception as e:
        print(f"❌ Report generation failed: {e}")
        sys.exit(1)
