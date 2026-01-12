#!/usr/bin/env python3
"""Validate astrological calculations against known values."""
import json
import subprocess
import sys

# Test case: June 15, 1990, 12:00 PM EDT, New York, NY
test_data = {
    "profile": {
        "name": "Validation Test",
        "date_of_birth": "1990-06-15",
        "time_of_birth": "12:00:00",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "timezone": "America/New_York",
    }
}

# Call the API
result = subprocess.run(
    [
        "curl",
        "-s",
        "-X",
        "POST",
        "https://astromeric-backend-production.up.railway.app/v2/profiles/natal",
        "-H",
        "Content-Type: application/json",
        "-d",
        json.dumps(test_data),
    ],
    capture_output=True,
    text=True,
)

try:
    data = json.loads(result.stdout)
except json.JSONDecodeError:
    print("ERROR: Could not parse response")
    print(result.stdout)
    sys.exit(1)

if data.get("status") != "success":
    print("ERROR:", data.get("detail") or data.get("error"))
    sys.exit(1)

chart = data["data"].get("chart_data", {})

print("=" * 70)
print("YOUR APP'S CALCULATIONS")
print("=" * 70)
print(f"Birth Data: June 15, 1990, 12:00 PM EDT")
print(
    f"Location: New York, NY ({test_data['profile']['latitude']}, {test_data['profile']['longitude']})"
)
print()

print("PLANETARY POSITIONS:")
print("-" * 70)
planets = [
    "sun",
    "moon",
    "mercury",
    "venus",
    "mars",
    "jupiter",
    "saturn",
    "uranus",
    "neptune",
    "pluto",
]
for planet in planets:
    p = chart.get(planet, {})
    sign = p.get("sign", "N/A")
    degree = p.get("degree", 0)
    print(f"  {planet.title():10s}: {sign:12s} {degree:6.2f}°")

print()
print("ANGLES:")
print("-" * 70)
for angle in ["ascendant", "midheaven"]:
    a = chart.get(angle, {})
    sign = a.get("sign", "N/A")
    degree = a.get("degree", 0)
    print(f"  {angle.title():10s}: {sign:12s} {degree:6.2f}°")

print()
print("=" * 70)
print("COMPARISON WITH KNOWN ASTROLOGICAL DATA:")
print("=" * 70)
print("For someone born June 15, 1990 around noon in New York:")
print()
print("Expected (from Swiss Ephemeris / astro.com standards):")
print("  Sun should be: Gemini (~24°)")
print("  Moon: Varies by exact time, typically Aquarius/Pisces")
print("  Mercury: Gemini or Cancer")
print("  Venus: Taurus or Gemini")
print("  Mars: Pisces or Aries")
print()

# Calculate basic validation
issues = []
sun = chart.get("sun", {})
if sun.get("sign") != "Gemini":
    issues.append(f"⚠️  Sun sign mismatch: got {sun.get('sign')}, expected Gemini")
if sun.get("degree", 0) < 20 or sun.get("degree", 0) > 28:
    issues.append(
        f"⚠️  Sun degree unusual: {sun.get('degree', 0):.2f}° (expected ~23-25°)"
    )

if issues:
    print("\n❌ VALIDATION ISSUES FOUND:")
    for issue in issues:
        print(f"  {issue}")
    print("\n⚠️  Your app may have calculation errors!")
else:
    print("\n✅ BASIC VALIDATION PASSED")
    print("   Sun position matches expected values")
    print("   (Full validation requires comparing all planetary positions)")
