FROM python:3.11-slim

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy source code
WORKDIR /app
COPY . /app

EXPOSE 8000

CMD ["uvicorn", "business_intel_scraper.backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
