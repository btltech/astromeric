"""
test_validators.py
------------------
Comprehensive tests for input validation.
"""

import pytest
from datetime import datetime, timedelta

from app.validators import (
    ValidationError,
    validate_latitude,
    validate_longitude,
    validate_date_of_birth,
    validate_time_of_birth,
    validate_timezone,
    validate_house_system,
    validate_name,
    validate_profile_data,
    validate_coordinates,
)


class TestValidateLatitude:
    """Tests for latitude validation."""

    def test_valid_latitude_zero(self):
        assert validate_latitude(0.0) == 0.0

    def test_valid_latitude_positive(self):
        assert validate_latitude(45.5) == 45.5

    def test_valid_latitude_negative(self):
        assert validate_latitude(-33.8) == -33.8

    def test_valid_latitude_extreme_north(self):
        assert validate_latitude(90.0) == 90.0

    def test_valid_latitude_extreme_south(self):
        assert validate_latitude(-90.0) == -90.0

    def test_none_returns_zero(self):
        assert validate_latitude(None) == 0.0

    def test_invalid_too_high(self):
        with pytest.raises(ValidationError) as exc:
            validate_latitude(91.0)
        assert "out of valid range" in exc.value.message

    def test_invalid_too_low(self):
        with pytest.raises(ValidationError) as exc:
            validate_latitude(-91.0)
        assert "out of valid range" in exc.value.message

    def test_invalid_string(self):
        with pytest.raises(ValidationError) as exc:
            validate_latitude("north")
        assert "Invalid latitude" in exc.value.message


class TestValidateLongitude:
    """Tests for longitude validation."""

    def test_valid_longitude_zero(self):
        assert validate_longitude(0.0) == 0.0

    def test_valid_longitude_positive(self):
        assert validate_longitude(120.5) == 120.5

    def test_valid_longitude_negative(self):
        assert validate_longitude(-74.0) == -74.0

    def test_valid_longitude_extreme_east(self):
        assert validate_longitude(180.0) == 180.0

    def test_valid_longitude_extreme_west(self):
        assert validate_longitude(-180.0) == -180.0

    def test_none_returns_zero(self):
        assert validate_longitude(None) == 0.0

    def test_invalid_too_high(self):
        with pytest.raises(ValidationError) as exc:
            validate_longitude(181.0)
        assert "out of valid range" in exc.value.message

    def test_invalid_too_low(self):
        with pytest.raises(ValidationError) as exc:
            validate_longitude(-181.0)
        assert "out of valid range" in exc.value.message


class TestValidateDateOfBirth:
    """Tests for date of birth validation."""

    def test_valid_date(self):
        assert validate_date_of_birth("1990-05-15") == "1990-05-15"

    def test_valid_date_early_year(self):
        assert validate_date_of_birth("1850-01-01") == "1850-01-01"

    def test_valid_date_recent(self):
        today = datetime.now().strftime("%Y-%m-%d")
        assert validate_date_of_birth(today) == today

    def test_empty_date_raises(self):
        with pytest.raises(ValidationError) as exc:
            validate_date_of_birth("")
        assert "required" in exc.value.message.lower()

    def test_none_date_raises(self):
        with pytest.raises(ValidationError) as exc:
            validate_date_of_birth(None)
        assert "required" in exc.value.message.lower()

    def test_invalid_format_slash(self):
        with pytest.raises(ValidationError) as exc:
            validate_date_of_birth("1990/05/15")
        assert "Invalid date format" in exc.value.message

    def test_invalid_format_short_year(self):
        with pytest.raises(ValidationError) as exc:
            validate_date_of_birth("90-05-15")
        assert "Invalid date format" in exc.value.message

    def test_invalid_month(self):
        with pytest.raises(ValidationError) as exc:
            validate_date_of_birth("1990-13-15")
        assert "Invalid date" in exc.value.message

    def test_invalid_day(self):
        with pytest.raises(ValidationError) as exc:
            validate_date_of_birth("1990-02-30")
        assert "Invalid date" in exc.value.message

    def test_future_date_raises(self):
        future = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        with pytest.raises(ValidationError) as exc:
            validate_date_of_birth(future)
        assert "future" in exc.value.message.lower()

    def test_too_old_date_raises(self):
        with pytest.raises(ValidationError) as exc:
            validate_date_of_birth("1700-01-01")
        assert "before" in exc.value.message.lower()


class TestValidateTimeOfBirth:
    """Tests for time of birth validation."""

    def test_valid_time_24h(self):
        assert validate_time_of_birth("14:30") == "14:30"

    def test_valid_time_midnight(self):
        assert validate_time_of_birth("00:00") == "00:00"

    def test_valid_time_noon(self):
        assert validate_time_of_birth("12:00") == "12:00"

    def test_valid_time_end_of_day(self):
        assert validate_time_of_birth("23:59") == "23:59"

    def test_valid_time_single_digit_hour(self):
        assert validate_time_of_birth("9:30") == "09:30"

    def test_valid_time_with_seconds(self):
        assert validate_time_of_birth("14:30:45") == "14:30"

    def test_none_returns_none(self):
        assert validate_time_of_birth(None) is None

    def test_invalid_hour_too_high(self):
        with pytest.raises(ValidationError) as exc:
            validate_time_of_birth("25:00")
        assert "hour" in exc.value.message.lower()

    def test_invalid_minute_too_high(self):
        with pytest.raises(ValidationError) as exc:
            validate_time_of_birth("14:60")
        assert "minute" in exc.value.message.lower()

    def test_invalid_format(self):
        with pytest.raises(ValidationError) as exc:
            validate_time_of_birth("2:30 PM")
        assert "Invalid time format" in exc.value.message


class TestValidateTimezone:
    """Tests for timezone validation."""

    def test_utc(self):
        assert validate_timezone("UTC") == "UTC"

    def test_gmt(self):
        assert validate_timezone("GMT") == "GMT"

    def test_iana_format(self):
        assert validate_timezone("America/New_York") == "America/New_York"

    def test_offset_format(self):
        assert validate_timezone("+05:30") == "+05:30"

    def test_none_returns_utc(self):
        assert validate_timezone(None) == "UTC"

    def test_empty_returns_utc(self):
        assert validate_timezone("") == "UTC"


class TestValidateHouseSystem:
    """Tests for house system validation."""

    def test_placidus_default(self):
        assert validate_house_system(None) == "Placidus"

    def test_placidus_explicit(self):
        assert validate_house_system("Placidus") == "Placidus"

    def test_whole_sign(self):
        assert validate_house_system("Whole") == "Whole Sign"

    def test_equal(self):
        assert validate_house_system("Equal") == "Equal"

    def test_koch(self):
        assert validate_house_system("Koch") == "Koch"

    def test_case_insensitive(self):
        assert validate_house_system("PLACIDUS") == "Placidus"

    def test_invalid_system(self):
        with pytest.raises(ValidationError) as exc:
            validate_house_system("InvalidSystem")
        assert "Unsupported" in exc.value.message


class TestValidateName:
    """Tests for name validation."""

    def test_valid_name(self):
        assert validate_name("John Doe") == "John Doe"

    def test_name_with_spaces(self):
        assert validate_name("  John Doe  ") == "John Doe"

    def test_single_name(self):
        assert validate_name("John") == "John"

    def test_empty_name_raises(self):
        with pytest.raises(ValidationError) as exc:
            validate_name("")
        assert "required" in exc.value.message.lower()

    def test_none_name_raises(self):
        with pytest.raises(ValidationError) as exc:
            validate_name(None)
        assert "required" in exc.value.message.lower()

    def test_whitespace_only_raises(self):
        with pytest.raises(ValidationError) as exc:
            validate_name("   ")
        assert "required" in exc.value.message.lower()

    def test_too_long_name_raises(self):
        long_name = "A" * 101
        with pytest.raises(ValidationError) as exc:
            validate_name(long_name)
        assert "too long" in exc.value.message.lower()


class TestValidateProfileData:
    """Tests for complete profile validation."""

    def test_valid_complete_profile(self):
        profile = {
            "name": "John Doe",
            "date_of_birth": "1990-05-15",
            "time_of_birth": "14:30",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "timezone": "America/New_York",
            "house_system": "Placidus",
        }
        result = validate_profile_data(profile)
        assert result["name"] == "John Doe"
        assert result["date_of_birth"] == "1990-05-15"
        assert result["latitude"] == 40.7128

    def test_minimal_profile(self):
        profile = {
            "name": "Jane",
            "date_of_birth": "1985-12-25",
        }
        result = validate_profile_data(profile)
        assert result["name"] == "Jane"
        assert result["latitude"] == 0.0  # Default
        assert result["timezone"] == "UTC"  # Default

    def test_missing_required_field_raises(self):
        profile = {
            "name": "John",
            # missing date_of_birth
        }
        with pytest.raises(ValidationError):
            validate_profile_data(profile)


class TestValidateCoordinates:
    """Tests for coordinate pair validation."""

    def test_valid_coordinates(self):
        lat, lon = validate_coordinates(40.7128, -74.0060)
        assert lat == 40.7128
        assert lon == -74.0060

    def test_none_coordinates(self):
        lat, lon = validate_coordinates(None, None)
        assert lat == 0.0
        assert lon == 0.0

    def test_invalid_lat_raises(self):
        with pytest.raises(ValidationError):
            validate_coordinates(100.0, -74.0)

    def test_invalid_lon_raises(self):
        with pytest.raises(ValidationError):
            validate_coordinates(40.0, -200.0)


class TestValidationErrorClass:
    """Tests for ValidationError exception class."""

    def test_error_attributes(self):
        error = ValidationError("field", "message", "suggestion")
        assert error.field == "field"
        assert error.message == "message"
        assert error.suggestion == "suggestion"

    def test_to_dict(self):
        error = ValidationError("latitude", "Invalid value", "Use -90 to 90")
        result = error.to_dict()
        assert result["field"] == "latitude"
        assert result["message"] == "Invalid value"
        assert result["suggestion"] == "Use -90 to 90"

    def test_str_representation(self):
        error = ValidationError("field", "error message")
        assert "field" in str(error)
        assert "error message" in str(error)
