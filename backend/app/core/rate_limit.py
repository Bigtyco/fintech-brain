import time
from collections import defaultdict
from fastapi import HTTPException, Request, status


class RateLimiter:
    """Simple in-memory rate limiter keyed by client IP."""

    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)

    def __call__(self, request: Request) -> None:
        now = time.time()
        key = request.client.host if request.client else "unknown"
        hits = self._hits[key]

        # prune expired entries
        self._hits[key] = [t for t in hits if now - t < self.window]

        if len(self._hits[key]) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"请求过于频繁，请 {self.window} 秒后重试",
            )
        self._hits[key].append(now)


login_rate_limiter = RateLimiter(max_requests=5, window_seconds=60)
