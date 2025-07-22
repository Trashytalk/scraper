#!/bin/bash

# Business Intelligence Scraper Demo
echo "🚀 Starting Business Intelligence Scraper Demo..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Start services in background
echo "📡 Starting Redis..."
if ! docker ps | grep -q redis; then
    docker run -d -p 6379:6379 --name redis-demo redis:7 || {
        echo "❌ Failed to start Redis. Make sure Docker is running."
        exit 1
    }
fi

echo "🔧 Starting API server..."
cd business_intel_scraper
uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

echo "⏳ Waiting for API to start..."
sleep 5

echo "🕷️  Running example scraper..."
curl -X POST http://localhost:8000/scrape || {
    echo "❌ Failed to start scraper"
    kill $API_PID 2>/dev/null
    exit 1
}

echo "✅ Demo started successfully!"
echo "🌐 API: http://localhost:8000"
echo "📊 Health check: curl http://localhost:8000/"
echo "📈 View jobs: curl http://localhost:8000/jobs"
echo ""
echo "Press Ctrl+C to stop the demo"

# Wait for interrupt
trap "echo '🛑 Stopping demo...'; kill $API_PID 2>/dev/null; docker stop redis-demo 2>/dev/null; docker rm redis-demo 2>/dev/null; exit 0" INT
wait $API_PID
