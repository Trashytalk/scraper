"""Analytics Middleware for automatic metrics collection."""

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from ..analytics.metrics import metrics_collector


class AnalyticsMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically collect analytics from API requests."""

    async def dispatch(self, request: Request, call_next):
        # Record request start time
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate request duration
        duration = time.time() - start_time

        # Record metrics
        await metrics_collector.record_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            duration=duration,
        )

        return response
