"""
Rate limiting middleware for the FastAPI backend.
Prevents abuse and ensures fair usage of API resources.
"""

import time
from collections import defaultdict
from functools import wraps
from typing import Callable, Dict, Tuple

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


class RateLimiter:
    """
    Token bucket rate limiter.

    Args:
        requests_per_minute: Maximum requests allowed per minute
        burst_size: Maximum burst size (defaults to requests_per_minute)
    """

    def __init__(self, requests_per_minute: int = 60, burst_size: int = None):
        self.rate = requests_per_minute / 60.0  # tokens per second
        self.burst_size = burst_size or requests_per_minute
        self.tokens: Dict[str, float] = defaultdict(lambda: self.burst_size)
        self.last_update: Dict[str, float] = defaultdict(time.time)

    def _get_client_id(self, request: Request) -> str:
        """Extract client identifier from request."""
        # Try X-Forwarded-For for proxied requests
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # Fall back to direct client IP
        return request.client.host if request.client else "unknown"

    def _refill_tokens(self, client_id: str) -> None:
        """Refill tokens based on time elapsed."""
        now = time.time()
        elapsed = now - self.last_update[client_id]
        self.tokens[client_id] = min(
            self.burst_size, self.tokens[client_id] + elapsed * self.rate
        )
        self.last_update[client_id] = now

    def is_allowed(self, request: Request) -> Tuple[bool, Dict]:
        """
        Check if request is allowed under rate limit.

        Returns:
            Tuple of (allowed: bool, headers: dict with rate limit info)
        """
        client_id = self._get_client_id(request)
        self._refill_tokens(client_id)

        headers = {
            "X-RateLimit-Limit": str(self.burst_size),
            "X-RateLimit-Remaining": str(int(self.tokens[client_id])),
            "X-RateLimit-Reset": str(
                int(
                    time.time() + (self.burst_size - self.tokens[client_id]) / self.rate
                )
            ),
        }

        if self.tokens[client_id] >= 1:
            self.tokens[client_id] -= 1
            return True, headers

        headers["Retry-After"] = str(int(1 / self.rate))
        return False, headers


# Global rate limiter instances
default_limiter = RateLimiter(requests_per_minute=60)
strict_limiter = RateLimiter(
    requests_per_minute=10, burst_size=5
)  # For expensive operations


async def rate_limit_middleware(request: Request, call_next):
    """
    FastAPI middleware for rate limiting.
    Add to app with: app.middleware("http")(rate_limit_middleware)
    """
    # Skip rate limiting for OPTIONS (preflight) and health checks
    if request.method == "OPTIONS" or request.url.path in [
        "/health",
        "/",
        "/docs",
        "/openapi.json",
    ]:
        return await call_next(request)

    allowed, headers = default_limiter.is_allowed(request)

    if not allowed:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "Rate limit exceeded. Please slow down.",
                "retry_after": headers.get("Retry-After", "60"),
            },
            headers=headers,
        )

    response = await call_next(request)

    # Add rate limit headers to response
    for key, value in headers.items():
        response.headers[key] = value

    return response


def rate_limit(requests_per_minute: int = 30):
    """
    Decorator for rate limiting specific endpoints.
    Works with FastAPI dependency injection - does not require request as first arg.

    Usage:
        @router.post("/register")
        @rate_limit(requests_per_minute=5)
        def register(user_data: UserCreate, db: Session = Depends(get_db)):
            ...
    """
    limiter = RateLimiter(requests_per_minute=requests_per_minute)

    def decorator(func: Callable):
        import asyncio
        import inspect

        # Check if the original function is async
        is_async = asyncio.iscoroutinefunction(func)

        @wraps(func)
        async def async_wrapper(*args, request: Request = None, **kwargs):
            # Try to find request in args or kwargs
            req = request
            if req is None:
                for arg in args:
                    if isinstance(arg, Request):
                        req = arg
                        break
            if req is None:
                for v in kwargs.values():
                    if isinstance(v, Request):
                        req = v
                        break

            # If we found a request, apply rate limiting
            if req is not None:
                allowed, headers = limiter.is_allowed(req)
                if not allowed:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Rate limit exceeded for this endpoint.",
                        headers=headers,
                    )

            # Call the original function
            if is_async:
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, request: Request = None, **kwargs):
            # Try to find request in args or kwargs
            req = request
            if req is None:
                for arg in args:
                    if isinstance(arg, Request):
                        req = arg
                        break
            if req is None:
                for v in kwargs.values():
                    if isinstance(v, Request):
                        req = v
                        break

            # If we found a request, apply rate limiting
            if req is not None:
                allowed, headers = limiter.is_allowed(req)
                if not allowed:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Rate limit exceeded for this endpoint.",
                        headers=headers,
                    )

            return func(*args, **kwargs)

        # Return appropriate wrapper based on function type
        return async_wrapper if is_async else sync_wrapper

    return decorator
