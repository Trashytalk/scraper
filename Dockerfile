# Dockerfile for Business Intelligence Scraper
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    wget \
    gnupg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt

# Install additional performance monitoring dependencies
RUN pip install --no-cache-dir \
    psutil \
    redis \
    aioredis \
    cachetools

# Copy application code
COPY . /app

# Create necessary directories
RUN mkdir -p /app/data/logs /app/data/output /app/data/jobs

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash scraper \
    && chown -R scraper:scraper /app
USER scraper

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/api/health || exit 1

# Expose port
EXPOSE $PORT

# Command to run the application
CMD ["uvicorn", "business_intel_scraper.backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
