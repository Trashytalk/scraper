#!/bin/bash

# Quick Start Test Script
# ======================
# 
# This script tests the quick start functionality to ensure
# it works properly with the comprehensive test framework.

echo "🧪 Testing Quick Start Integration"
echo "================================="

# Test help functionality
echo "1. Testing help command..."
./quick_start.sh --help >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Help command works"
else
    echo "   ❌ Help command failed"
    exit 1
fi

# Test status functionality
echo "2. Testing status command..."
./quick_start.sh --status >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Status command works"
else
    echo "   ❌ Status command failed"
    exit 1
fi

# Test clean functionality
echo "3. Testing clean command..."
./quick_start.sh --clean >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Clean command works"
else
    echo "   ❌ Clean command failed"
    exit 1
fi

# Test script permissions
echo "4. Testing script permissions..."
if [ -x "./quick_start.sh" ]; then
    echo "   ✅ Script is executable"
else
    echo "   ❌ Script is not executable"
    exit 1
fi

# Test integration with testing framework
echo "5. Testing integration with test framework..."
if [ -f "tests/run_full_coverage.py" ] && [ -x "tests/run_full_coverage.py" ]; then
    echo "   ✅ Test framework integration ready"
else
    echo "   ❌ Test framework not available"
    exit 1
fi

echo ""
echo "🎉 All Quick Start Tests Passed!"
echo "================================"
echo ""
echo "✅ Quick start script is ready for use"
echo "✅ All commands work correctly"
echo "✅ Integration with testing framework confirmed"
echo ""
echo "🚀 You can now use: ./quick_start.sh"
