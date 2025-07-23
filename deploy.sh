#!/bin/bash

# Production Deployment Script for Business Intelligence Scraper
# This script sets up and deploys the entire application stack

set -e

echo "🚀 Starting Business Intelligence Scraper Production Deployment..."

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data/logs data/output data/jobs logs/nginx docker/grafana/dashboards docker/grafana/datasources

# Set proper permissions
echo "🔐 Setting permissions..."
chmod 700 secrets/
chmod 600 secrets/*.txt

# Generate additional secrets if they don't exist
if [ ! -f secrets/jwt_secret.txt ]; then
    echo "🔑 Generating JWT secret..."
    python3 -c "import secrets; print(secrets.token_urlsafe(43))" > secrets/jwt_secret.txt
fi

if [ ! -f secrets/postgres_password.txt ]; then
    echo "🔑 Generating PostgreSQL password..."
    echo "scraper_db_$(openssl rand -hex 16)" > secrets/postgres_password.txt
fi

if [ ! -f secrets/grafana_password.txt ]; then
    echo "🔑 Generating Grafana password..."
    echo "admin_$(openssl rand -hex 12)" > secrets/grafana_password.txt
fi

# Build and start services
echo "🔨 Building Docker images..."
docker-compose -f docker-compose.prod.yml build

echo "🚀 Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🏥 Checking service health..."
services=("scraper-api" "scraper-redis" "scraper-postgres")

for service in "${services[@]}"; do
    if docker-compose -f docker-compose.prod.yml ps "$service" | grep -q "Up (healthy)"; then
        echo "✅ $service is healthy"
    else
        echo "⚠️  $service might not be fully ready yet"
    fi
done

# Display access information
echo ""
echo "🎉 Deployment completed!"
echo ""
echo "📊 Access Information:"
echo "   API Server:     http://localhost:8000"
echo "   API Docs:       http://localhost:8000/docs"
echo "   Frontend:       http://localhost:3000"
echo "   Grafana:        http://localhost:3001"
echo "   Prometheus:     http://localhost:9090"
echo ""
echo "🔐 Admin Credentials:"
echo "   API Admin:      admin / admin123"
echo "   Grafana Admin:  admin / $(cat secrets/grafana_password.txt)"
echo ""
echo "📝 Logs:"
echo "   View API logs:     docker-compose -f docker-compose.prod.yml logs scraper-api"
echo "   View all logs:     docker-compose -f docker-compose.prod.yml logs"
echo ""
echo "🛑 To stop all services:"
echo "   docker-compose -f docker-compose.prod.yml down"
echo ""
echo "✅ Production deployment is ready!"
