#!/bin/bash

# Script to start both backend and frontend servers for the BI Scraper

echo "=== Starting Business Intelligence Scraper Servers ==="

# Function to kill background processes on exit
cleanup() {
    echo "Cleaning up processes..."
    jobs -p | xargs -r kill
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Run database migrations
echo "Running database migrations..."
cd business_intel_scraper/backend/db
alembic upgrade head
cd ../../..

# Start backend server
echo "Starting backend server on port 8000..."
python -m uvicorn business_intel_scraper.backend.api.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend server
echo "Starting frontend server..."
cd business_intel_scraper/frontend
npm install
npm run dev &
FRONTEND_PID=$!

echo ""
echo "=== Servers Started ==="
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Keep script running and wait for both processes
wait $BACKEND_PID $FRONTEND_PID
