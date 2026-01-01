"""
Security headers middleware for the FastAPI backend.
Adds essential security headers to all responses.
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse, HTMLResponse, PlainTextResponse


async def security_headers_middleware(request: Request, call_next):
    """
    Middleware to add security headers to all responses.
    """
    response = await call_next(request)
    
    # Add security headers
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    # Content-Security-Policy - adjust based on your needs
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "  # Allow inline scripts for now, but consider removing unsafe
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' https://fonts.googleapis.com https://fonts.gstatic.com; "
        "connect-src 'self' https://api.openai.com https://generativelanguage.googleapis.com; "  # Adjust for your APIs
        "frame-ancestors 'none';"  # Prevent embedding
    )
    
    return response