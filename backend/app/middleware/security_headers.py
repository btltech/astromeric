"""
Security headers middleware for the FastAPI backend.
Adds essential security headers to all responses.
Uses centralized config from config.py for CSP management.
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse, HTMLResponse, PlainTextResponse
from ..config import SECURITY_HEADERS


async def security_headers_middleware(request: Request, call_next):
    """
    Middleware to add security headers to all responses.
    Headers are loaded from config.py for centralized management.
    """
    response = await call_next(request)
    
    # Add all security headers from config
    for header_name, header_value in SECURITY_HEADERS.items():
        response.headers[header_name] = header_value
    
    return response