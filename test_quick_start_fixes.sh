#!/bin/bash

# Test script to verify quick_start.sh fixes
# This script tests the corrected endpoints and ports

echo "🧪 Testing Quick Start Fixes"
echo "============================"
echo

# Test 1: Check if backend server is configured correctly
echo "Test 1: Backend server configuration"
if grep -q "curl -f http://localhost:\$BACKEND_PORT/api/health" quick_start.sh; then
    echo "✅ Health endpoint corrected to /api/health"
else
    echo "❌ Health endpoint still using old /health"
fi

# Test 2: Check if frontend port is corrected
echo "Test 2: Frontend port configuration"
if grep -q "FRONTEND_PORT=5173" quick_start.sh; then
    echo "✅ Frontend port corrected to 5173"
else
    echo "❌ Frontend port still using 5174"
fi

# Test 3: Check if Vite config is using correct port
echo "Test 3: Vite configuration"
if grep -q "port: 5173" business_intel_scraper/frontend/vite.config.js; then
    echo "✅ Vite configured for port 5173"
else
    echo "❌ Vite not configured for port 5173"
fi

# Test 4: Check if backend uses correct health endpoint
echo "Test 4: Backend health endpoint"
if grep -q "@app.get(\"/api/health\")" backend_server.py; then
    echo "✅ Backend serves health at /api/health"
else
    echo "❌ Backend health endpoint not found"
fi

echo
echo "🔧 Testing complete! If all tests pass, quick_start.sh should work better."
echo "💡 To test the actual startup:"
echo "   ./quick_start.sh"
echo
echo "🌐 Expected URLs after startup:"
echo "   Frontend: http://localhost:5173/"
echo "   Backend:  http://localhost:8000/docs"
echo "   Health:   http://localhost:8000/api/health"
