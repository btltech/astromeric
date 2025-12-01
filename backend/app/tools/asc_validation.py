"""
asc_validation.py
Utility script to print Ascendant and house cusps for manual comparison with astro.com/Astro-Seek.

Usage:
    python asc_validation.py

Place Swiss Ephemeris files in /app/ephemeris (or set EPHEMERIS_PATH) before running.
Update TEST_PROFILES with birth data you want to validate against trusted sources.
"""

from __future__ import annotations

import json

# Import via package so this script should be run as:
#   python -m backend.app.tools.asc_validation
from ..chart_service import build_natal_chart

TEST_PROFILES = [
    {
        "name": "Sample1",
        "date_of_birth": "1990-03-15",
        "time_of_birth": "08:15",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "timezone": "America/New_York",
    },
    {
        "name": "Sample2",
        "date_of_birth": "1985-07-22",
        "time_of_birth": "22:45",
        "latitude": 51.5074,
        "longitude": -0.1278,
        "timezone": "Europe/London",
    },
    {
        "name": "Sample3",
        "date_of_birth": "1978-11-05",
        "time_of_birth": "13:30",
        "latitude": -33.8688,
        "longitude": 151.2093,
        "timezone": "Australia/Sydney",
    },
]


def summarize_chart(profile):
    chart = build_natal_chart(profile)
    houses = {
        h["house"]: {"sign": h["sign"], "degree": round(h["degree"], 2)}
        for h in chart["houses"]
    }
    asc = houses.get(1)
    planets = {
        p["name"]: {
            "sign": p["sign"],
            "degree": round(p["degree"], 2),
            "house": p["house"],
        }
        for p in chart["planets"]
    }
    aspects = chart["aspects"][:10]
    return {
        "metadata": chart["metadata"],
        "ascendant": asc,
        "houses": houses,
        "planets": planets,
        "aspects": aspects,
    }


if __name__ == "__main__":
    report = {p["name"]: summarize_chart(p) for p in TEST_PROFILES}
    print(json.dumps(report, indent=2))
