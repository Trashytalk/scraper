#!/bin/bash
"""
Main Directory Cleanup Script
=============================

This script organizes the main directory by moving files to appropriate locations
and creating a clean, consolidated structure.

Author: Business Intelligence Scraper Cleanup
Date: July 25, 2025
"""

set -e

echo "🧹 Starting Main Directory Cleanup..."
echo "======================================"

# Create necessary directories if they don't exist
mkdir -p archive/legacy_docs
mkdir -p archive/legacy_tests  
mkdir -p archive/legacy_scripts
mkdir -p archive/legacy_configs
mkdir -p archive/deprecated

echo "📁 Moving legacy documentation files..."

# Move old documentation files to archive
legacy_docs=(
    "ADDITIONAL_TESTING_RECOMMENDATIONS.md"
    "BACKEND_TESTING_REPORT.md"
    "COMPREHENSIVE_ASSESSMENT_REPORT.md"
    "COMPREHENSIVE_TESTING_UPDATE_SUMMARY.md"
    "CRAWLER_TO_SCRAPER_IMPLEMENTATION.md"
    "CRAWLER_TO_SCRAPER_PIPELINE.md"
    "ERROR_HANDLING_SUMMARY.md"
    "FRONTEND_FIXED_SCRAPING_GUIDE.md"
    "FRONTEND_TESTING_REPORT.md"
    "IMPLEMENTATION_ROADMAP.md"
    "IMPROVEMENT_ROADMAP.md"
    "INCOMPLETE_FUNCTIONS_ANALYSIS.md"
    "MINOR_IMPROVEMENTS_COMPLETE.md"
    "PAGINATION_AND_CENTRALIZED_DATA.md"
    "PHASE_1_IMPLEMENTATION_SUMMARY.md"
    "PHASE_2_IMPLEMENTATION_SUMMARY.md"
    "PRE_IMPLEMENTATION_TESTING_GUIDE.md"
    "PRIORITY_2_CODE_ORGANIZATION_SUMMARY.md"
    "PRIORITY_4_DATA_PROCESSING_COMPLETE.md"
    "PRIORITY_6_FRONTEND_PERFORMANCE_COMPLETE.md"
    "PRIORITY_7_SECURITY_HARDENING_COMPLETE.md"
    "PRIORITY_8_TESTING_STRATEGY_COMPLETE.md"
    "PRIORITY_IMPLEMENTATION_COMPLETE.md"
    "README_UPDATES_SUMMARY.md"
    "README_v1.0.0.md"
    "REAL_WORLD_TESTING_GUIDE.md"
    "REAL_WORLD_TESTING_SUCCESS.md"
    "REPOSITORY_CLEANUP_SUMMARY.md"
    "REPOSITORY_CORRECTIONS_SUMMARY.md"
    "ROADMAP_COMPLETE_SUMMARY.md"
    "SETUP_COMPLETE.md"
    "TESTING_STRATEGY.md"
)

for doc in "${legacy_docs[@]}"; do
    if [ -f "$doc" ]; then
        echo "  📄 Moving $doc"
        mv "$doc" "archive/legacy_docs/"
    fi
done

echo "🧪 Moving legacy test files..."

# Move old test files to archive
legacy_tests=(
    "comprehensive_test_suite.py"
    "pre_implementation_tests.py"
    "quick_error_test.py"
    "quick_test.py"
    "test_crawler_to_scraper.py"
    "test_data_processing_pipeline.py"
    "test_database_config.py"
    "test_error_handling.py"
    "test_gui_integration.py"
    "test_minor_improvements.py"
    "test_minor_improvements_simple.py"
    "test_pagination.py"
    "test_scraping.py"
    "test_security.py"
    "test_server_startup.py"
    "test_url_extraction.py"
)

for test in "${legacy_tests[@]}"; do
    if [ -f "$test" ]; then
        echo "  🧪 Moving $test"
        mv "$test" "archive/legacy_tests/"
    fi
done

echo "📜 Moving legacy scripts..."

# Move old scripts to archive
legacy_scripts=(
    "cleanup_repo.sh"
    "dev-setup.sh"
    "final_demo.sh"
    "quick_start.sh"
    "start_servers.sh"
    "test_system.sh"
    "validate_setup.py"
    "verify_system.py"
    "final_status_report.py"
    "implementation_complete_summary.py"
)

for script in "${legacy_scripts[@]}"; do
    if [ -f "$script" ]; then
        echo "  📜 Moving $script"
        mv "$script" "archive/legacy_scripts/"
    fi
done

echo "⚙️ Moving legacy configuration files..."

# Move old config files to archive
legacy_configs=(
    "requirements-consolidated.txt"
    "requirements-testing.txt"
    "docker-compose.dev.yml"
    "docker-compose.prod.yml"
    "docker-compose.production.yml"
    "simple_api_server.py"
)

for config in "${legacy_configs[@]}"; do
    if [ -f "$config" ]; then
        echo "  ⚙️ Moving $config"
        mv "$config" "archive/legacy_configs/"
    fi
done

echo "🗑️ Moving deprecated files..."

# Move deprecated files
deprecated_files=(
    "analytics.db"
    "data.db"
    "coverage.xml"
)

for file in "${deprecated_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  🗑️ Moving $file"
        mv "$file" "archive/deprecated/"
    fi
done

echo "🧹 Cleaning up empty cache directories..."

# Remove cache directories
cache_dirs=(
    "__pycache__"
    ".mypy_cache"
    ".pytest_cache"
    ".ruff_cache"
    "htmlcov"
    "http_cache"
)

for cache_dir in "${cache_dirs[@]}"; do
    if [ -d "$cache_dir" ]; then
        echo "  🧹 Removing $cache_dir"
        rm -rf "$cache_dir"
    fi
done

# Remove test research project (if it exists)
if [ -d "test-research-project" ]; then
    echo "  🧹 Removing test-research-project"
    rm -rf "test-research-project"
fi

# Remove venv if it exists (should use .venv)
if [ -d "venv" ]; then
    echo "  🧹 Removing old venv directory"
    rm -rf "venv"
fi

echo ""
echo "✅ Main Directory Cleanup Complete!"
echo "=================================="
echo ""
echo "📁 Organized structure:"
echo "  📋 Current docs: README.md, QUICKSTART.md, CONTRIBUTING.md, etc."
echo "  📦 Archive created with legacy files organized by type"
echo "  🧪 Active tests in tests/ directory"
echo "  🐳 Active docker configs: docker-compose.yml, Dockerfile"
echo "  ⚙️ Core configs: requirements.txt, pyproject.toml, pytest.ini"
echo ""
echo "🎯 Main directory is now clean and consolidated!"
