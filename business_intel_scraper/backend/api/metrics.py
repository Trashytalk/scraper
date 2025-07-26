from __future__ import annotations

import time
from typing import Callable, Awaitable

from prometheus_client import Counter, Histogram, make_asgi_app
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

REQUEST_COUNT = Counter(
    "bi_api_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint"],
)
REQUEST_LATENCY = Histogram(
    "bi_api_request_duration_seconds",
    "HTTP request latency in seconds",
    ["endpoint"],
)


class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        path = request.url.path
        REQUEST_COUNT.labels(method=request.method, endpoint=path).inc()
        REQUEST_LATENCY.labels(endpoint=path).observe(time.perf_counter() - start)
        return response


metrics_app = make_asgi_app()
