#!/bin/bash
# Health check script for Docker container
curl -f http://localhost:${PORT:-8000}/api/health || exit 1
