#!/bin/bash
# Repository Cleanup Script
# This script organizes and removes unnecessary files from the main directory

echo "🧹 Starting repository cleanup..."
echo

# Create directories for organization
echo "📁 Creating organizational directories..."
mkdir -p archive/documentation
mkdir -p archive/testing  
mkdir -p archive/databases
mkdir -p temp/

# Move redundant documentation to archive
echo "📚 Archiving redundant documentation..."
mv ADVANCED_CRAWLING_SUMMARY.md archive/documentation/ 2>/dev/null
mv CLEANUP_COMPLETE.md archive/documentation/ 2>/dev/null
mv CONSOLIDATION_SUMMARY.md archive/documentation/ 2>/dev/null
mv IMPLEMENTATION_COMPLETE.md archive/documentation/ 2>/dev/null
mv IMPLEMENTATION_SUCCESS.md archive/documentation/ 2>/dev/null
mv IMPLEMENTATION_SUMMARY.md archive/documentation/ 2>/dev/null
mv MAINTENANCE_COMPLETED.md archive/documentation/ 2>/dev/null
mv MAINTENANCE_REPORT.md archive/documentation/ 2>/dev/null
mv MAINTENANCE_SESSION_COMPLETE.md archive/documentation/ 2>/dev/null
mv PERFORMANCE_IMPLEMENTATION_SUMMARY.md archive/documentation/ 2>/dev/null
mv PHASE1_IMPLEMENTATION_COMPLETE.md archive/documentation/ 2>/dev/null
mv LIVE_TESTING_READY.md archive/documentation/ 2>/dev/null
mv TYPE_IMPROVEMENTS_REPORT.md archive/documentation/ 2>/dev/null
mv TYPE_STATUS_UPDATE.md archive/documentation/ 2>/dev/null
mv VISUALIZATION_INTEGRATION_GUIDE.md archive/documentation/ 2>/dev/null
mv README_OLD.md archive/documentation/ 2>/dev/null
mv README_NEW.md archive/documentation/ 2>/dev/null

# Move test databases to archive
echo "🗄️ Archiving test databases..."
mv analytics.db archive/databases/ 2>/dev/null
mv real_world_test.db archive/databases/ 2>/dev/null
mv test_database.db archive/databases/ 2>/dev/null
mv test_final.db archive/databases/ 2>/dev/null

# Keep data.db in main directory as it's the active database

# Move standalone test files to tests directory
echo "🧪 Moving test files to tests directory..."
mv test_*.py tests/ 2>/dev/null

# Move demo and setup scripts to scripts directory
echo "📜 Creating scripts directory..."
mkdir -p scripts/
mv demo.sh scripts/ 2>/dev/null  
mv demo_*.py scripts/ 2>/dev/null
mv setup.sh scripts/ 2>/dev/null
mv setup_*.py scripts/ 2>/dev/null
mv create-project.sh scripts/ 2>/dev/null
mv final_status_report.sh scripts/ 2>/dev/null
mv start_real_world_testing.sh scripts/ 2>/dev/null
mv setup_visual_analytics.sh scripts/ 2>/dev/null

# Move utility Python files to scripts
mv check_performance_status.py scripts/ 2>/dev/null
mv database_success_test.py scripts/ 2>/dev/null
mv final_success_report.py scripts/ 2>/dev/null
mv implementation_summary.py scripts/ 2>/dev/null
mv maintenance_fix.py scripts/ 2>/dev/null
mv simple_validation.py scripts/ 2>/dev/null

# Clean up temporary files and caches
echo "🗑️ Removing temporary files and caches..."
rm -rf __pycache__/ 2>/dev/null
rm -rf .pytest_cache/ 2>/dev/null
rm -rf .mypy_cache/ 2>/dev/null
rm -rf htmlcov/ 2>/dev/null
rm -rf http_cache/ 2>/dev/null
rm -f coverage.xml 2>/dev/null

# Clean up mysterious files that seem to be version numbers
echo "🔢 Removing orphaned version files..."
rm -f "=1.1.0" "=1.12.0" "=1.21.0" "=2.2.0" "=3.4.0" "=4.20.0" 2>/dev/null

# Move logs to a proper location
echo "📝 Organizing logs..."
if [ -d "logs" ]; then
    mkdir -p data/logs
    mv logs/* data/logs/ 2>/dev/null
    rmdir logs 2>/dev/null
fi

# Create .gitignore entries for new structure
echo "📋 Updating .gitignore..."
cat >> .gitignore << 'EOF'

# Archive directories
archive/
temp/

# Database files
*.db
!data/schema.sql

# Cache directories
__pycache__/
.pytest_cache/
.mypy_cache/
htmlcov/
http_cache/

# IDE files
.vscode/
.idea/
*.swp
*.swo

# Log files
data/logs/*.log

# Coverage files
coverage.xml
.coverage
EOF

echo
echo "✅ Cleanup complete! Repository structure:"
echo
ls -la | grep -E "^d" | awk '{print "📁 " $9}'
echo
echo "📄 Remaining files in root:"
ls -la | grep -E "^-" | grep -v "\.git" | awk '{print "   " $9}' | head -20
echo
echo "🎯 Main directory is now clean and organized!"
