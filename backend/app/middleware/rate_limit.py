"""
Rate limiting middleware for the FastAPI backend.
Prevents abuse and ensures fair usage of API resources.
"""

import os
import time
from collections import defaultdict
from functools import wraps
from typing import Callable, Dict, Optional, Tuple

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
        """Extract client identifier from request.

        X-Forwarded-For is only trusted when the request originates from a
        known proxy (Cloudflare).  Trusting it blindly allows attackers to
        spoof the header and bypass IP-based rate limiting.
        """
        # Cloudflare sets CF-Connecting-IP to the real visitor IP and cannot
        # be spoofed by the client.  Prefer it when present.
        cf_ip = request.headers.get("CF-Connecting-IP")
        if cf_ip:
            return cf_ip.strip()

        # Railway / other trusted reverse proxies: use the rightmost
        # non-private IP in X-Forwarded-For (the last hop the proxy added),
        # NOT the leftmost which is client-controlled.
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ips = [ip.strip() for ip in forwarded.split(",") if ip.strip()]
            if ips:
                return ips[-1]  # rightmost = added by the trusted proxy

        # Fall back to direct client IP
        return request.client.host if request.client else "unknown"

    def _refill_tokens(self, client_id: str) -> None:
        """Refill tokens based on time elapsed."""
        now = time.time()
        if client_id not in self.last_update:
            self.last_update[client_id] = now
            return

        elapsed = max(0.0, now - self.last_update[client_id])
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
        if (
            os.getenv("PYTEST_CURRENT_TEST")
            or os.getenv("TESTING") == "1"
            or os.getenv("ENVIRONMENT") == "test"
        ):
            if not os.getenv("TEST_RATE_LIMITING"):
                return True, {}

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

# Auth-specific limiters — tighter limits to block brute-force and spam
login_limiter = RateLimiter(requests_per_minute=5, burst_size=5)
register_limiter = RateLimiter(requests_per_minute=3, burst_size=3)
password_reset_limiter = RateLimiter(requests_per_minute=3, burst_size=3)


class DailyRateLimiter:
    """
    Sliding window daily rate limiter (true 24-hour window).
    """

    def __init__(self, limit: int):
        self.limit = limit
        # Maps client_id -> list of float timestamps of successful requests
        self.requests: Dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, client_id: str) -> Tuple[bool, Dict[str, str]]:
        if (
            os.getenv("PYTEST_CURRENT_TEST")
            or os.getenv("TESTING") == "1"
            or os.getenv("ENVIRONMENT") == "test"
        ):
            if not os.getenv("TEST_RATE_LIMITING"):
                return True, {}

        now = time.time()
        window_start = now - 86400.0  # 24 hours ago

        # Filter out timestamps older than 24 hours
        self.requests[client_id] = [
            t for t in self.requests[client_id] if t > window_start
        ]

        remaining = self.limit - len(self.requests[client_id])

        if remaining > 0:
            self.requests[client_id].append(now)
            remaining -= 1
            headers = {
                "X-RateLimit-Limit": str(self.limit),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(int(now + 86400.0)),
            }
            return True, headers
        else:
            # Limit exceeded. The oldest request in the window dictates the reset time.
            oldest_request = self.requests[client_id][0]
            reset_time = int(oldest_request + 86400.0)
            retry_after = max(1, int(reset_time - now))

            headers = {
                "X-RateLimit-Limit": str(self.limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_time),
                "Retry-After": str(retry_after),
            }
            return False, headers


# Daily sliding-window limiters (limit = 1 for Gemini, 3 for general services)
gemini_daily_limiter = DailyRateLimiter(limit=1)
general_daily_limiter = DailyRateLimiter(limit=3)


def get_user_id_from_request(request: Request) -> Optional[str]:
    """Extract user ID from JWT token in the Authorization header."""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None

    parts = auth_header.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        token = parts[1]
        try:
            from backend.app.auth import decode_token

            token_data = decode_token(token)
            if token_data and token_data.user_id:
                return str(token_data.user_id)
        except Exception:
            pass
    return None


def get_client_ip(request: Request) -> str:
    """Extract client IP from request."""
    cf_ip = request.headers.get("CF-Connecting-IP")
    if cf_ip:
        return cf_ip.strip()

    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        ips = [ip.strip() for ip in forwarded.split(",") if ip.strip()]
        if ips:
            return ips[-1]

    return request.client.host if request.client else "unknown"


async def rate_limit_middleware(request: Request, call_next):
    """
    FastAPI middleware for rate limiting.
    Add to app with: app.middleware("http")(rate_limit_middleware)
    """
    path = request.url.path

    # 1. OPTIONS bypass
    if request.method == "OPTIONS":
        return await call_next(request)

    # 2. Path bypasses
    if path in ["/", "/health", "/docs", "/openapi.json"]:
        return await call_next(request)

    if (
        os.getenv("PYTEST_CURRENT_TEST")
        or os.getenv("TESTING") == "1"
        or os.getenv("ENVIRONMENT") == "test"
    ):
        if not os.getenv("TEST_RATE_LIMITING"):
            return await call_next(request)

    # Resolve client ID: user ID if logged in, else real client IP
    user_id = get_user_id_from_request(request)
    client_id = user_id if user_id else get_client_ip(request)

    # Check if request is from a native mobile app (iOS or Android)
    from app.ai_service import is_native_app

    is_app = is_native_app(request)

    # 3. Auth endpoints (login/register/reset-password)
    if "login" in path:
        allowed, headers = login_limiter.is_allowed(request)
        limit_name = "Login"
    elif "register" in path:
        allowed, headers = register_limiter.is_allowed(request)
        limit_name = "Registration"
    elif (
        "reset-password" in path
        or "forgot-password" in path
        or "verify-email" in path
        or "resend-verification" in path
    ):
        allowed, headers = password_reset_limiter.is_allowed(request)
        limit_name = "Auth Reset"
    # 4. Gemini endpoints
    elif path in [
        "/v2/ai/explain",
        "/v2/cosmic-guide/chat",
        "/v2/cosmic-guide/guidance",
        "/v2/cosmic-guide/interpret",
    ]:
        if is_app:
            allowed, headers = default_limiter.is_allowed(request)
            limit_name = "Gemini AI (app)"
        else:
            allowed, headers = gemini_daily_limiter.is_allowed(client_id)
            limit_name = "Gemini AI"
    # 5. Everything else under the API (including unknown routes)
    else:
        if is_app:
            allowed, headers = default_limiter.is_allowed(request)
            limit_name = "Core Services (app)"
        else:
            allowed, headers = general_daily_limiter.is_allowed(client_id)
            limit_name = "Core Services"

    if not allowed:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": f"Rate limit exceeded for {limit_name}. Please slow down.",
                "retry_after": headers.get("Retry-After", "86400"),
                "reset_time": headers.get("X-RateLimit-Reset", ""),
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
