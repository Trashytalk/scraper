#!/bin/bash
set -e

echo "🚀 Starting Business Intelligence Scraper..."

# Wait for database to be ready
if [ "$DATABASE_URL" ]; then
    echo "⏳ Waiting for database..."
    python -c "
import time
import os
import sys
try:
    if 'postgresql' in os.getenv('DATABASE_URL', ''):
        import psycopg2
        from urllib.parse import urlparse
        url = urlparse(os.getenv('DATABASE_URL'))
        conn = psycopg2.connect(
            host=url.hostname,
            port=url.port,
            user=url.username,
            password=url.password,
            database=url.path[1:]
        )
        conn.close()
        print('✅ Database connection successful')
    else:
        print('✅ Using SQLite database')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    sys.exit(1)
"
fi

# Wait for Redis to be ready (if configured)
if [ "$REDIS_URL" ]; then
    echo "⏳ Waiting for Redis..."
    python -c "
import redis
import os
import sys
try:
    r = redis.from_url(os.getenv('REDIS_URL'))
    r.ping()
    print('✅ Redis connection successful')
except Exception as e:
    print(f'❌ Redis connection failed: {e}')
    sys.exit(1)
"
fi

# Run database migrations if needed
echo "🔄 Running database migrations..."
python -c "
try:
    from backend_server import create_tables
    create_tables()
    print('✅ Database tables created/updated')
except Exception as e:
    print(f'⚠️ Database migration warning: {e}')
"

# Start the application
echo "🌟 Starting application server..."
if [ "$1" = "worker" ]; then
    echo "🔄 Starting background worker..."
    exec celery -A backend_server worker --loglevel=INFO
elif [ "$1" = "scheduler" ]; then
    echo "⏰ Starting task scheduler..."
    exec celery -A backend_server beat --loglevel=INFO
else
    echo "🖥️ Starting web server..."
    exec gunicorn backend_server:app \
        --bind 0.0.0.0:${PORT:-8000} \
        --workers ${WORKERS:-4} \
        --worker-class uvicorn.workers.UvicornWorker \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --preload \
        --access-logfile - \
        --error-logfile - \
        --log-level INFO \
        --timeout 300 \
        --keep-alive 5
fi
