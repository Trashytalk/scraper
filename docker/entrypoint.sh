#!/bin/bash
# Production Entrypoint Script
# Business Intelligence Scraper

set -e

echo "🚀 Starting Business Intelligence Scraper - Production Mode"
echo "=================================================="

# Environment validation
if [ -z "$ENVIRONMENT" ]; then
    export ENVIRONMENT=production
fi

# Create necessary directories
mkdir -p /app/data /app/logs /app/secrets
chown -R appuser:appuser /app/data /app/logs

# Database initialization
echo "📊 Initializing database..."
if [ ! -f "/app/data/data.db" ]; then
    echo "Creating new database..."
    python3 -c "
import sqlite3
import os
from datetime import datetime

# Create database
conn = sqlite3.connect('/app/data/data.db')
cursor = conn.cursor()

# Create tables (basic structure)
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    url TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS job_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER,
    data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs (id)
)
''')

# Create default admin user
import hashlib
password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
cursor.execute('INSERT OR IGNORE INTO users (username, password_hash) VALUES (?, ?)', ('admin', password_hash))

conn.commit()
conn.close()
print('Database initialized successfully')
"
    chown appuser:appuser /app/data/data.db
else
    echo "Database already exists"
fi

# Configuration validation
echo "🔧 Validating configuration..."
python3 -c "
from config.advanced_config_manager import ConfigManager
import sys

try:
    config_manager = ConfigManager()
    config = config_manager.get_config()
    print(f'✅ Configuration loaded: {config.environment}')
    print(f'✅ Database URL: {config.database.url}')
    print(f'✅ Redis URL: {config.redis.url}')
except Exception as e:
    print(f'❌ Configuration error: {e}')
    sys.exit(1)
"

# Redis preparation
echo "🔄 Preparing Redis..."
if [ ! -f "/app/data/dump.rdb" ]; then
    touch /app/data/dump.rdb
    chown redis:redis /app/data/dump.rdb
fi

# Log rotation setup
echo "📝 Setting up log rotation..."
cat > /etc/logrotate.d/app << EOF
/app/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    copytruncate
    su appuser appuser
}
EOF

# Health check script
echo "🏥 Creating health check script..."
cat > /app/healthcheck.sh << 'EOF'
#!/bin/bash
set -e

# Check backend API
if ! curl -f -s http://localhost:8000/api/health > /dev/null; then
    echo "Backend API health check failed"
    exit 1
fi

# Check Redis
if ! redis-cli -h 127.0.0.1 -p 6379 ping > /dev/null 2>&1; then
    echo "Redis health check failed"
    exit 1
fi

# Check Nginx
if ! curl -f -s http://localhost:80/api/health > /dev/null; then
    echo "Nginx health check failed"
    exit 1
fi

echo "All services healthy"
exit 0
EOF

chmod +x /app/healthcheck.sh
chown appuser:appuser /app/healthcheck.sh

# Start services based on command
echo "🎯 Starting services..."
if [ "$1" = "supervisord" ]; then
    echo "Starting all services with Supervisor..."
    exec "$@"
elif [ "$1" = "backend-only" ]; then
    echo "Starting backend only..."
    exec python3 backend_server.py
elif [ "$1" = "shell" ]; then
    echo "Starting shell..."
    exec /bin/bash
else
    echo "Starting with custom command: $@"
    exec "$@"
fi
