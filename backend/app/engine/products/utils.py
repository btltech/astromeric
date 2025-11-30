from __future__ import annotations

from datetime import date as date_cls
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from ..charts.models import ChartRequest, Location
from .types import ProfileInput


def parse_datetime(date_str: str, time_str: Optional[str], timezone: str) -> datetime:
    """Parse a date/time pair into a timezone-aware datetime."""
    time_component = time_str if time_str else "12:00"
    dt = datetime.fromisoformat(f"{date_str}T{time_component}")
    tz = ZoneInfo(timezone) if timezone else None
    if dt.tzinfo and tz:
        return dt.astimezone(tz)
    if tz:
        return dt.replace(tzinfo=tz)
    return dt


def build_chart_request(
    profile: ProfileInput,
    chart_type: str,
    target_date: Optional[str] = None,
    time_override: Optional[str] = None,
) -> ChartRequest:
    """Convert profile data into a ChartRequest for the chart engine."""
    date_part = target_date or profile.date_of_birth
    time_part = time_override or profile.time_of_birth
    dt = parse_datetime(date_part, time_part, profile.timezone)
    location = Location(
        latitude=profile.latitude or 0.0,
        longitude=profile.longitude or 0.0,
        timezone=profile.timezone or "UTC",
    )
    return ChartRequest(chart_type=chart_type, datetime=dt, location=location)


def pick_scope_date(scope: str, base_date: Optional[str] = None) -> str:
    """Pick the anchor date for a given scope."""
    if base_date:
        return base_date
    today = date_cls.today()
    return today.isoformat()
