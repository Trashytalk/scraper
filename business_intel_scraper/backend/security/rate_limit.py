"""Request rate limiting middleware."""

from __future__ import annotations

from collections import defaultdict, deque
from time import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import HTTP_429_TOO_MANY_REQUESTS


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Limit requests per IP or user using a sliding window."""

    def __init__(self, app, limit: int = 60, window: int = 60) -> None:
        super().__init__(app)
        self.limit = limit
        self.window = window
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    def _key(self, request: Request) -> str:
        user = request.headers.get("Authorization")
        if user:
            return f"user:{user}"
        client_ip = request.client.host
        return f"ip:{client_ip}"

    async def dispatch(self, request: Request, call_next) -> Response:
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
