"""Request rate limiting middleware."""

from __future__ import annotations

from collections import defaultdict, deque
from time import time
from typing import Callable, Awaitable, Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import HTTP_429_TOO_MANY_REQUESTS


class RateLimiter:
    """Rate limiter for controlling request frequency"""

    def __init__(self, limit: int = 60, window: int = 60):
        self.limit = limit
        self.window = window
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    def is_allowed(self, key: str) -> bool:
        """Check if a request is allowed for the given key"""
        now = time()
        window_start = now - self.window

        # Clean old requests
        requests = self._requests[key]
        while requests and requests[0] < window_start:
            requests.popleft()

        # Check if under limit
        if len(requests) < self.limit:
            requests.append(now)
            return True
        return False


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Limit requests per IP or user using a sliding window."""

    def __init__(
        self, app: Callable[..., Any], limit: int = 60, window: int = 60
    ) -> None:
        super().__init__(app)
        self.limit = limit
        self.window = window
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    def _key(self, request: Request) -> str:
        user = request.headers.get("Authorization")
        if user:
            return f"user:{user}"
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        key = self._key(request)
        now = time()
        history = self._requests[key]
        cutoff = now - self.window
        while history and history[0] <= cutoff:
            history.popleft()
        if len(history) >= self.limit:
            return Response("Too Many Requests", status_code=HTTP_429_TOO_MANY_REQUESTS)
        history.append(now)
        return await call_next(request)
