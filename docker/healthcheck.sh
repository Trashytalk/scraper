#!/bin/bash
# Health check script for queue system containers

set -e

# Determine the service type based on environment variables
SERVICE_TYPE=${SERVICE_TYPE:-"api"}
WORKER_TYPE=${WORKER_TYPE:-""}

case "$SERVICE_TYPE" in
    "api")
        # Check if the API is responding
        curl -f http://localhost:8000/health || exit 1
        ;;
    "worker")
        # Check worker health based on type
        case "$WORKER_TYPE" in
            "crawl"|"parse")
                # Check if worker process is running
                pgrep -f "queue.worker.*--type $WORKER_TYPE" > /dev/null || exit 1
                ;;
            *)
                echo "Unknown worker type: $WORKER_TYPE"
                exit 1
                ;;
        esac
        ;;
    "monitor")
        # Check if monitor service is responding
        curl -f http://localhost:8080/health || exit 1
        ;;
    *)
        echo "Unknown service type: $SERVICE_TYPE"
        exit 1
        ;;
esac

echo "Health check passed for $SERVICE_TYPE"
exit 0
