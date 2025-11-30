"""Product layer builds concrete outputs on top of the generic engine."""

from .types import ProfileInput
from .natal import build_natal_profile
from .forecast import build_forecast
from .compatibility import build_compatibility_report

__all__ = [
    "ProfileInput",
    "build_natal_profile",
    "build_forecast",
    "build_compatibility_report",
]
