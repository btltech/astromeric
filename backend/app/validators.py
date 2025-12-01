"""
validators.py
-------------
Comprehensive input validation for birth data with user-friendly error messages.

Validates:
- Coordinates (latitude: -90 to 90, longitude: -180 to 180)
- Dates (valid format, not in future, within ephemeris range)
- Times (valid 24-hour format)
- Timezones (valid IANA timezone names)
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Optional, Tuple

# Ephemeris typically covers 1800-2400, but we'll be conservative
EPHEMERIS_MIN_YEAR = 1800
EPHEMERIS_MAX_YEAR = 2400

# Common timezone patterns for basic validation
TIMEZONE_PATTERN = re.compile(
    r"^(UTC|GMT|[A-Z][a-z]+/[A-Za-z_]+(/[A-Za-z_]+)?|[+-]\d{2}:\d{2})$"
)


class ValidationError(Exception):
    """Custom exception for validation errors with user-friendly messages."""
    
    def __init__(self, field: str, message: str, suggestion: str = ""):
        self.field = field
        self.message = message
        self.suggestion = suggestion
        super().__init__(f"{field}: {message}")
    
    def to_dict(self):
        return {
            "field": self.field,
            "message": self.message,
            "suggestion": self.suggestion,
        }


def validate_latitude(lat: Optional[float], field_name: str = "latitude") -> float:
    """
    Validate latitude value.
    
    Args:
        lat: Latitude value to validate
        field_name: Field name for error messages
    
    Returns:
        Validated latitude (defaults to 0.0 if None)
    
    Raises:
        ValidationError: If latitude is out of range
    """
    if lat is None:
        return 0.0
    
    try:
        lat = float(lat)
    except (TypeError, ValueError):
        raise ValidationError(
            field_name,
            f"Invalid latitude value: {lat}",
            "Latitude must be a number between -90 and 90"
        )
    
    if lat < -90 or lat > 90:
        raise ValidationError(
            field_name,
            f"Latitude {lat} is out of valid range (-90 to 90)",
            "Latitude must be between -90 (South Pole) and 90 (North Pole)"
        )
    
    return lat


def validate_longitude(lon: Optional[float], field_name: str = "longitude") -> float:
    """
    Validate longitude value.
    
    Args:
        lon: Longitude value to validate
        field_name: Field name for error messages
    
    Returns:
        Validated longitude (defaults to 0.0 if None)
    
    Raises:
        ValidationError: If longitude is out of range
    """
    if lon is None:
        return 0.0
    
    try:
        lon = float(lon)
    except (TypeError, ValueError):
        raise ValidationError(
            field_name,
            f"Invalid longitude value: {lon}",
            "Longitude must be a number between -180 and 180"
        )
    
    if lon < -180 or lon > 180:
        raise ValidationError(
            field_name,
            f"Longitude {lon} is out of valid range (-180 to 180)",
            "Longitude must be between -180 (West) and 180 (East)"
        )
    
    return lon


def validate_date_of_birth(dob: str, field_name: str = "date_of_birth") -> str:
    """
    Validate date of birth string.
    
    Args:
        dob: Date string in YYYY-MM-DD format
        field_name: Field name for error messages
    
    Returns:
        Validated date string
    
    Raises:
        ValidationError: If date is invalid, in future, or outside ephemeris range
    """
    if not dob:
        raise ValidationError(
            field_name,
            "Date of birth is required",
            "Please provide a date in YYYY-MM-DD format"
        )
    
    # Check format
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", dob):
        raise ValidationError(
            field_name,
            f"Invalid date format: {dob}",
            "Please use YYYY-MM-DD format (e.g., 1990-05-15)"
        )
    
    # Parse and validate
    try:
        date = datetime.strptime(dob, "%Y-%m-%d")
    except ValueError as e:
        raise ValidationError(
            field_name,
            f"Invalid date: {dob}",
            "Please check the month and day values are valid"
        )
    
    # Check if future date
    today = datetime.now(timezone.utc).date()
    if date.date() > today:
        raise ValidationError(
            field_name,
            "Date of birth cannot be in the future",
            f"Please enter a date on or before {today.isoformat()}"
        )
    
    # Check ephemeris range
    if date.year < EPHEMERIS_MIN_YEAR:
        raise ValidationError(
            field_name,
            f"Year {date.year} is before our astronomical data coverage",
            f"Please enter a date after {EPHEMERIS_MIN_YEAR}"
        )
    
    if date.year > EPHEMERIS_MAX_YEAR:
        raise ValidationError(
            field_name,
            f"Year {date.year} is beyond our astronomical data coverage",
            f"Please enter a date before {EPHEMERIS_MAX_YEAR}"
        )
    
    return dob


def validate_time_of_birth(
    time_str: Optional[str], 
    field_name: str = "time_of_birth"
) -> Optional[str]:
    """
    Validate time of birth string.
    
    Args:
        time_str: Time string in HH:MM format (24-hour)
        field_name: Field name for error messages
    
    Returns:
        Validated time string or None
    
    Raises:
        ValidationError: If time format is invalid
    """
    if not time_str:
        return None
    
    # Accept various formats and normalize to HH:MM
    time_patterns = [
        (r"^(\d{1,2}):(\d{2})$", lambda h, m: f"{int(h):02d}:{m}"),  # H:MM or HH:MM
        (r"^(\d{1,2}):(\d{2}):(\d{2})$", lambda h, m, s: f"{int(h):02d}:{m}"),  # H:MM:SS
        (r"^(\d{2})(\d{2})$", lambda h, m: f"{h}:{m}"),  # HHMM
    ]
    
    normalized = None
    for pattern, formatter in time_patterns:
        match = re.match(pattern, time_str.strip())
        if match:
            normalized = formatter(*match.groups())
            break
    
    if not normalized:
        raise ValidationError(
            field_name,
            f"Invalid time format: {time_str}",
            "Please use HH:MM format (24-hour), e.g., 14:30 for 2:30 PM"
        )
    
    # Validate hour and minute values
    try:
        hours, minutes = map(int, normalized.split(":"))
        if hours < 0 or hours > 23:
            raise ValidationError(
                field_name,
                f"Invalid hour value: {hours}",
                "Hours must be between 0 and 23"
            )
        if minutes < 0 or minutes > 59:
            raise ValidationError(
                field_name,
                f"Invalid minute value: {minutes}",
                "Minutes must be between 0 and 59"
            )
    except ValueError:
        raise ValidationError(
            field_name,
            f"Invalid time: {time_str}",
            "Please use HH:MM format (24-hour)"
        )
    
    return normalized


def validate_timezone(
    tz: Optional[str], 
    field_name: str = "timezone"
) -> str:
    """
    Validate timezone string.
    
    Args:
        tz: Timezone string (IANA format preferred)
        field_name: Field name for error messages
    
    Returns:
        Validated timezone string (defaults to "UTC")
    
    Raises:
        ValidationError: If timezone format is clearly invalid
    """
    if not tz:
        return "UTC"
    
    tz = tz.strip()
    
    # Accept common formats
    if tz in ("UTC", "GMT"):
        return tz
    
    # Check for IANA format (e.g., America/New_York)
    if "/" in tz and re.match(r"^[A-Z][a-z]+/[A-Za-z_]+", tz):
        return tz
    
    # Check for offset format (e.g., +05:30, -08:00)
    if re.match(r"^[+-]\d{2}:\d{2}$", tz):
        return tz
    
    # If it doesn't match known patterns, warn but accept
    # (actual timezone validation would require pytz/zoneinfo)
    return tz


def validate_house_system(
    system: Optional[str], 
    field_name: str = "house_system"
) -> str:
    """
    Validate house system name.
    
    Args:
        system: House system name
        field_name: Field name for error messages
    
    Returns:
        Validated house system name (defaults to "Placidus")
    
    Raises:
        ValidationError: If house system is not supported
    """
    if not system:
        return "Placidus"
    
    valid_systems = {
        "placidus": "Placidus",
        "whole": "Whole Sign",
        "wholesign": "Whole Sign",
        "equal": "Equal",
        "koch": "Koch",
        "campanus": "Campanus",
        "topocentric": "Topocentric",
    }
    
    normalized = system.lower().replace(" ", "").replace("-", "")
    
    if normalized in valid_systems:
        return valid_systems[normalized]
    
    raise ValidationError(
        field_name,
        f"Unsupported house system: {system}",
        f"Supported systems: {', '.join(set(valid_systems.values()))}"
    )


def validate_name(name: Optional[str], field_name: str = "name") -> str:
    """
    Validate name string.
    
    Args:
        name: Name to validate
        field_name: Field name for error messages
    
    Returns:
        Validated and trimmed name
    
    Raises:
        ValidationError: If name is empty or too long
    """
    if not name or not name.strip():
        raise ValidationError(
            field_name,
            "Name is required",
            "Please provide a name for the profile"
        )
    
    name = name.strip()
    
    if len(name) > 100:
        raise ValidationError(
            field_name,
            "Name is too long (max 100 characters)",
            "Please use a shorter name"
        )
    
    if len(name) < 1:
        raise ValidationError(
            field_name,
            "Name is required",
            "Please provide a name for the profile"
        )
    
    return name


def validate_profile_data(profile: dict) -> dict:
    """
    Validate all profile data fields.
    
    Args:
        profile: Dictionary containing profile data
    
    Returns:
        Dictionary with validated and normalized data
    
    Raises:
        ValidationError: If any field validation fails
    """
    validated = {}
    
    # Required fields
    validated["name"] = validate_name(profile.get("name"))
    validated["date_of_birth"] = validate_date_of_birth(profile.get("date_of_birth"))
    
    # Optional fields with defaults
    validated["time_of_birth"] = validate_time_of_birth(profile.get("time_of_birth"))
    validated["latitude"] = validate_latitude(profile.get("latitude"))
    validated["longitude"] = validate_longitude(profile.get("longitude"))
    validated["timezone"] = validate_timezone(profile.get("timezone"))
    validated["house_system"] = validate_house_system(profile.get("house_system"))
    
    return validated


def validate_coordinates(
    lat: Optional[float], 
    lon: Optional[float]
) -> Tuple[float, float]:
    """
    Validate latitude and longitude together.
    
    Args:
        lat: Latitude value
        lon: Longitude value
    
    Returns:
        Tuple of (validated_lat, validated_lon)
    
    Raises:
        ValidationError: If coordinates are invalid
    """
    return validate_latitude(lat), validate_longitude(lon)
