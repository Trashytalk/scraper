FROM python:3.11-slim

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy source code
WORKDIR /app
COPY . /app

CMD ["celery", "-A", "business_intel_scraper.backend.workers.tasks.celery_app", "worker", "--loglevel=info"]
