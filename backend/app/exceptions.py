"""
Custom exception classes and error handling for structured logging.
"""

import uuid
import logging
from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse
from datetime import datetime

logger = logging.getLogger(__name__)


class AstroError(Exception):
    """Base exception for all astro-related errors."""
    
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        field: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.field = field
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(AstroError):
    """Raised when input validation fails."""
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
    ):
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            field=field,
            details={"value": value},
        )


class InvalidDateError(AstroError):
    """Raised when date format or values are invalid."""
    def __init__(self, message: str, value: Optional[str] = None):
        super().__init__(
            code="INVALID_DATE",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            field="date_of_birth",
            details={"value": value},
        )


class InvalidCoordinatesError(AstroError):
    """Raised when latitude/longitude are invalid."""
    def __init__(self, message: str):
        super().__init__(
            code="INVALID_COORDINATES",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class EphemerisError(AstroError):
    """Raised when ephemeris calculation fails."""
    def __init__(self, message: str):
        super().__init__(
            code="EPHEMERIS_ERROR",
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class AuthenticationError(AstroError):
    """Raised when authentication fails."""
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            code="AUTHENTICATION_ERROR",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class AuthorizationError(AstroError):
    """Raised when user lacks required permissions."""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            code="AUTHORIZATION_ERROR",
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class ResourceNotFoundError(AstroError):
    """Raised when requested resource doesn't exist."""
    def __init__(self, resource: str, resource_id: Any):
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource, "id": str(resource_id)},
        )


class RateLimitError(AstroError):
    """Raised when rate limit is exceeded."""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            code="RATE_LIMIT_EXCEEDED",
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


# ============================================================================
# STRUCTURED LOGGING WITH REQUEST ID
# ============================================================================

class StructuredLogger:
    """Logger with automatic request ID tracking."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def _log(
        self,
        level: int,
        message: str,
        request_id: Optional[str] = None,
        **kwargs: Any,
    ):
        """Log with structured context."""
        # Don't include 'message' in kwargs as it's reserved by Python's logging
        safe_kwargs = {k: v for k, v in kwargs.items() if k != 'message'}
        context = {
            "request_id": request_id or "unknown",
            **safe_kwargs,
        }
        self.logger.log(level, f"[{context['request_id']}] {message}", extra=context)
    
    def info(self, message: str, request_id: Optional[str] = None, **kwargs):
        self._log(logging.INFO, message, request_id, **kwargs)
    
    def warning(self, message: str, request_id: Optional[str] = None, **kwargs):
        self._log(logging.WARNING, message, request_id, **kwargs)
    
    def error(self, message: str, request_id: Optional[str] = None, **kwargs):
        self._log(logging.ERROR, message, request_id, **kwargs)
    
    def debug(self, message: str, request_id: Optional[str] = None, **kwargs):
        self._log(logging.DEBUG, message, request_id, **kwargs)


# ============================================================================
# EXCEPTION HANDLER
# ============================================================================

async def astro_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle custom AstroError exceptions and other exceptions."""
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    
    # Log the error
    logger = StructuredLogger(__name__)
    
    # Handle AstroError exceptions
    if isinstance(exc, AstroError):
        logger.error(
            exc.message,
            request_id=request_id,
            code=exc.code,
            field=exc.field,
            status_code=exc.status_code,
        )
        
        response = {
            "status": "error",
            "error": {
                "code": exc.code,
                "message": exc.message,
                "field": exc.field,
                **exc.details,
            },
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        return JSONResponse(
            status_code=exc.status_code,
            content=response,
        )
    else:
        # Handle generic exceptions
        error_message = str(exc)
        logger.error(
            error_message,
            request_id=request_id,
            status_code=500,
        )
        
        response = {
            "status": "error",
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": error_message,
                "field": None,
            },
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        return JSONResponse(
            status_code=500,
            content=response,
        )


# ============================================================================
# REQUEST ID MIDDLEWARE
# ============================================================================

async def request_id_middleware(request: Request, call_next):
    """Add request ID to all requests for tracing."""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response
