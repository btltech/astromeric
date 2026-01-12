"""Request ID middleware for tracing requests."""

import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


async def request_id_middleware(request: Request, call_next):
    """Add unique request ID to each request for tracing."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
