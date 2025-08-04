#!/bin/bash
# Start Enhanced Server with Error Handling and Monitoring

echo "🚀 Starting Enhanced Business Intelligence Scraper Server"
echo "Environment: ${ENVIRONMENT:-development}"

# Set environment variables if not set
export ENVIRONMENT=${ENVIRONMENT:-development}
export DATABASE_URL=${DATABASE_URL:-sqlite:///./data.db}
export JWT_SECRET_KEY=${JWT_SECRET_KEY:-dev-secret-key-change-in-production}

# Kill any existing server
echo "🔄 Checking for existing server processes..."
pkill -f "python.*backend_server.py" 2>/dev/null || true

# Wait a moment
sleep 2

# Start the enhanced server
echo "📡 Starting enhanced server on port 8000..."
python3 backend_server.py &

# Get the process ID
SERVER_PID=$!
echo "✅ Server started with PID: $SERVER_PID"

# Wait for server to start
echo "⏳ Waiting for server to initialize..."
sleep 5

# Check if server is responding
echo "🔍 Testing server health..."
curl -s http://localhost:8000/api/health > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Server is responding!"
    echo "🌐 Health endpoint: http://localhost:8000/api/health"
    echo "📚 API docs: http://localhost:8000/docs"
    echo "🔧 Server PID: $SERVER_PID"
    echo ""
    echo "🧪 Ready to run test: python3 test_modal_debug.py"
else
    echo "❌ Server is not responding"
    kill $SERVER_PID 2>/dev/null
    exit 1
fi
