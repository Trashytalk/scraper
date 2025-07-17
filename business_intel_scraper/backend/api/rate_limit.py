"""Simple in-memory rate limiting middleware."""

from __future__ import annotations

from collections import defaultdict, deque
from time import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import HTTP_429_TOO_MANY_REQUESTS


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Limit number of requests per client within a time window."""

    def __init__(self, app, limit: int = 60, window: int = 60) -> None:
        super().__init__(app)
        self.limit = limit
        self.window = window
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next) -> Response:
        client_ip = request.client.host
        now = time()
        history = self._requests[client_ip]
        while history and now - history[0] > self.window:
            history.popleft()
        if len(history) >= self.limit:
            return Response(
                content="Too Many Requests",
                status_code=HTTP_429_TOO_MANY_REQUESTS,
            )
        history.append(now)
        return await call_next(request)
