"""
Standardized request/response schemas for API v2.
Ensures consistent structure across all endpoints.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from pydantic import BaseModel, Field

T = TypeVar("T")


# ============================================================================
# STANDARDIZED RESPONSE ENVELOPE
# ============================================================================


class ResponseStatus(str, Enum):
    """Standard response status values."""

    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"  # For partial failures


class ApiResponse(BaseModel, Generic[T]):
    """Standard API response envelope for all endpoints."""

    status: ResponseStatus
    data: Optional[T] = None
    error: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    request_id: Optional[str] = Field(
        None, description="Unique request ID for debugging"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "data": {"key": "value"},
                "message": "Operation completed successfully",
                "request_id": "req_abc123",
                "timestamp": "2026-01-01T13:54:00Z",
            }
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response."""

    items: List[T]
    total: int
    page: int
    page_size: int
    has_next: bool
    has_prev: bool

    @property
    def total_pages(self) -> int:
        return (self.total + self.page_size - 1) // self.page_size


# ============================================================================
# STANDARDIZED REQUEST MODELS
# ============================================================================


class ProfilePayload(BaseModel):
    """Standardized user profile data."""

    name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: str = Field(..., description="ISO format: YYYY-MM-DD")
    time_of_birth: Optional[str] = Field(
        None, description="HH:MM:SS or None for unknown"
    )
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    timezone: Optional[str] = None  # IANA timezone

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Jane Doe",
                "date_of_birth": "1990-06-15",
                "time_of_birth": "14:30:00",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "timezone": "America/New_York",
            }
        }


class NatalProfileRequest(BaseModel):
    """Request for natal profile calculation."""

    profile: ProfilePayload
    include_asteroids: bool = Field(
        False, description="Include minor planets (Chiron, etc.)"
    )
    include_aspects: bool = Field(True, description="Include planetary aspects")
    orb: float = Field(8.0, ge=1, le=20, description="Orb in degrees for aspects")


class ForecastRequest(BaseModel):
    """Request for forecast calculation."""

    profile: ProfilePayload
    scope: str = Field(..., pattern="^(daily|weekly|monthly|yearly)$")
    date: Optional[str] = Field(
        None, description="ISO format: YYYY-MM-DD (defaults to today)"
    )
    include_details: bool = Field(True)


class CompatibilityRequest(BaseModel):
    """Request for compatibility analysis."""

    person_a: ProfilePayload
    person_b: ProfilePayload
    relationship_type: str = Field(
        "romantic", pattern="^(romantic|friendship|business)$"
    )


class NumerologyRequest(BaseModel):
    """Request for numerology analysis."""

    profile: ProfilePayload
    include_extended: bool = Field(False, description="Include extended numerology")


# ============================================================================
# ERROR RESPONSE SCHEMAS
# ============================================================================


class ErrorDetail(BaseModel):
    """Detailed error information."""

    code: str = Field(..., description="Error code (e.g., INVALID_DATE)")
    message: str = Field(..., description="Human-readable error message")
    field: Optional[str] = Field(None, description="Field that caused the error")
    value: Optional[Any] = Field(None, description="Value that caused the error")


class ValidationErrorResponse(BaseModel):
    """Response for validation errors."""

    status: ResponseStatus = ResponseStatus.ERROR
    errors: List[ErrorDetail]
    request_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# COMMON FILTER/QUERY MODELS
# ============================================================================


class PaginationParams(BaseModel):
    """Standard pagination parameters."""

    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")
    sort_by: Optional[str] = None
    sort_order: str = Field("asc", pattern="^(asc|desc)$")


class DateRangeFilter(BaseModel):
    """Standard date range filter."""

    start_date: Optional[str] = Field(None, description="ISO format: YYYY-MM-DD")
    end_date: Optional[str] = Field(None, description="ISO format: YYYY-MM-DD")


# ============================================================================
# VERSION INFORMATION
# ============================================================================


class ApiVersionInfo(BaseModel):
    """API version information."""

    version: str
    status: str = "stable"  # stable, beta, deprecated
    deprecated_at: Optional[str] = None  # ISO datetime when deprecated
    sunset_at: Optional[str] = None  # ISO datetime when will be removed
    migration_guide: Optional[str] = None  # URL to migration guide


class ApiMetadata(BaseModel):
    """API metadata response."""

    versions: Dict[str, ApiVersionInfo]
    current_version: str
    health_status: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
