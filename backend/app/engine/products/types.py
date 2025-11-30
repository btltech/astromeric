from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class ProfileInput:
    name: str
    date_of_birth: str
    time_of_birth: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timezone: str = "UTC"
    preferred_topics: Optional[list[str]] = None
    language: str = "en"
