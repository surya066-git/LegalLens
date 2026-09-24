from __future__ import annotations

import threading
import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class SlidingWindowLimiter:
    def __init__(self) -> None:
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, key: str, limit: int, window_seconds: float) -> bool:
        from app.config import get_settings
        if get_settings().app_env == "test":
            return True
        now = time.monotonic()
        cutoff = now - window_seconds
        with self._lock:
            bucket = self._hits[key]
            while bucket and bucket[0] < cutoff:
                bucket.popleft()
            if len(bucket) >= limit:
                return False
            bucket.append(now)
            return True


_limiter = SlidingWindowLimiter()


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()[:128]
    if request.client:
        return request.client.host
    return "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
        from app.config import get_settings

        settings = get_settings()
        path = request.url.path.rstrip("/") or "/"
        method = request.method.upper()
        ip = client_ip(request)

        limit: int | None = None
        if method == "POST" and path == "/documents":
            limit = settings.rate_limit_upload_per_minute
            key = f"upload:{ip}"
        elif method == "POST" and path.endswith("/questions"):
            limit = settings.rate_limit_question_per_minute
            key = f"question:{ip}"
        else:
            key = ""

        if limit is not None and not _limiter.allow(key, limit, 60.0):
            return JSONResponse(
                status_code=429,
                content={
                    "detail": {
                        "code": "rate_limited",
                        "message": "Too many requests. Please wait a moment and try again.",
                    }
                },
            )

        return await call_next(request)
