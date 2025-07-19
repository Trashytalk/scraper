#!/bin/bash

# Project runner script
set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN_SCRAPER_ROOT="$(dirname "$PROJECT_ROOT")"

echo "🚀 Starting scraper project..."
echo "Project: $(basename "$PROJECT_ROOT")"

# Check if main scraper is available
if [ ! -f "$MAIN_SCRAPER_ROOT/setup.sh" ]; then
    echo "❌ Main scraper not found. Make sure this project is inside the scraper directory."
    exit 1
fi

# Source the project environment
if [ -f .env ]; then
    set -a
    source .env
    set +a
    echo "✓ Loaded project configuration"
fi

# Activate main scraper environment
if [ -f "$MAIN_SCRAPER_ROOT/.venv/bin/activate" ]; then
    source "$MAIN_SCRAPER_ROOT/.venv/bin/activate"
    echo "✓ Activated scraper environment"
else
    echo "❌ Scraper environment not found. Run setup.sh in main directory first."
    exit 1
fi

# Change to main scraper directory and run
cd "$MAIN_SCRAPER_ROOT"

echo "🔄 Starting API server..."
uvicorn business_intel_scraper.backend.api.main:app --host 0.0.0.0 --port 8000
