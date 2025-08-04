#!/bin/bash
# Enhanced Server Startup Script

echo "🚀 Starting Enhanced Business Intelligence Scraper Server"
echo "Environment: ${ENVIRONMENT:-development}"

# Set environment variables if not set
export ENVIRONMENT=${ENVIRONMENT:-development}
export DATABASE_URL=${DATABASE_URL:-sqlite:///./data.db}
export JWT_SECRET_KEY=${JWT_SECRET_KEY:-dev-secret-key-change-in-production}

# Start the server
echo "Starting server on port 8000..."
python3 backend_server.py

