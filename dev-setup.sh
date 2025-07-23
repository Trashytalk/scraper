#!/bin/bash

# Development Environment Setup Script
# Quick setup for local development with Docker

set -e

echo "🔧 Setting up development environment..."

# Check Docker availability
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Create development directories
echo "📁 Creating development directories..."
mkdir -p data/logs data/output data/jobs

# Generate minimal secrets for development
echo "🔑 Setting up development secrets..."
mkdir -p secrets
echo "dev_jwt_secret_$(date +%s)" > secrets/jwt_secret.txt
echo "dev_postgres_password" > secrets/postgres_password.txt
echo "dev_grafana_password" > secrets/grafana_password.txt

# Start development environment
echo "🚀 Starting development environment..."
docker-compose -f docker-compose.dev.yml up -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 15

# Check health
echo "🏥 Checking service health..."
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo "✅ API server is running"
else
    echo "⚠️  API server is not responding yet"
fi

echo ""
echo "🎉 Development environment is ready!"
echo ""
echo "📋 Available Services:"
echo "   API Server:    http://localhost:8000"
echo "   API Docs:      http://localhost:8000/docs"
echo "   Redis:         localhost:6379"
echo ""
echo "📝 Development Commands:"
echo "   View logs:     docker-compose -f docker-compose.dev.yml logs -f"
echo "   Stop services: docker-compose -f docker-compose.dev.yml down"
echo "   Restart API:   docker-compose -f docker-compose.dev.yml restart scraper-api"
echo ""
echo "🔧 The API server will auto-reload on code changes!"
