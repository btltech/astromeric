"""
transit_alerts.py
-----------------
Daily transit tracking and notification system.
Checks for major transits hitting natal chart positions.
"""

from __future__ import annotations

import logging
import os
import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional

from .chart_service import build_natal_chart, build_transit_chart

logger = logging.getLogger(__name__)

# Aspect orbs for transit alerts (tighter than natal)
TRANSIT_ORBS = {
    "conjunction": 2.0,
    "opposition": 2.0,
    "square": 1.5,
    "trine": 1.5,
    "sextile": 1.0,
}

# Major transiting planets to track
TRANSIT_PLANETS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

# Significant natal points to check
NATAL_POINTS = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Ascendant"]


def calculate_aspect(degree1: float, degree2: float) -> Optional[tuple[str, float]]:
    """
    Calculate if two degrees form an aspect.
    Returns (aspect_name, orb) or None.
    """
    diff = abs(degree1 - degree2)
    if diff > 180:
        diff = 360 - diff

    aspect_angles = {
        "conjunction": 0,
        "sextile": 60,
        "square": 90,
        "trine": 120,
        "opposition": 180,
    }

    for aspect_name, angle in aspect_angles.items():
        orb = abs(diff - angle)
        max_orb = TRANSIT_ORBS.get(aspect_name, 2.0)
        if orb <= max_orb:
            return (aspect_name, orb)

    return None


def get_absolute_degree(sign: str, degree: float) -> float:
    """Convert sign + degree to absolute zodiac degree (0-360)."""
    signs = [
        "Aries",
        "Taurus",
        "Gemini",
        "Cancer",
        "Leo",
        "Virgo",
        "Libra",
        "Scorpio",
        "Sagittarius",
        "Capricorn",
        "Aquarius",
        "Pisces",
    ]
    try:
        sign_index = signs.index(sign)
        return sign_index * 30 + degree
    except ValueError:
        return 0.0


def find_transit_aspects(
    natal_chart: Dict[str, Any],
    transit_chart: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Find aspects between transit planets and natal positions.

    Returns list of transit aspects with:
    - transit_planet: Name of transiting planet
    - natal_point: Natal planet or point being aspected
    - aspect: Type of aspect
    - orb: Exactness in degrees
    - applying: Whether aspect is applying (getting tighter) or separating
    """
    aspects = []

    natal_planets_list = natal_chart.get("planets", [])
    natal_planets = {p["name"]: p for p in natal_planets_list}

    transit_planets_list = transit_chart.get("planets", [])
    transit_planets = {p["name"]: p for p in transit_planets_list}

    # Check each transit planet against natal points
    for t_name in TRANSIT_PLANETS:
        t_planet = transit_planets.get(t_name)
        if not t_planet:
            continue

        t_degree = get_absolute_degree(t_planet["sign"], t_planet["degree"])

        for n_name in NATAL_POINTS:
            n_planet = natal_planets.get(n_name)
            if not n_planet:
                continue

            n_degree = get_absolute_degree(n_planet["sign"], n_planet["degree"])

            result = calculate_aspect(t_degree, n_degree)
            if result:
                aspect_name, orb = result
                aspects.append(
                    {
                        "transit_planet": t_name,
                        "natal_point": n_name,
                        "aspect": aspect_name,
                        "orb": round(orb, 2),
                        "transit_sign": t_planet["sign"],
                        "transit_degree": round(t_planet["degree"], 2),
                        "natal_sign": n_planet["sign"],
                        "natal_degree": round(n_planet["degree"], 2),
                    }
                )

    # Sort by orb (tightest first)
    aspects.sort(key=lambda x: x["orb"])

    return aspects


def get_transit_interpretation(transit: Dict[str, Any]) -> str:
    """Generate interpretation text for a transit aspect."""
    t_planet = transit["transit_planet"]
    n_point = transit["natal_point"]
    aspect = transit["aspect"]

    interpretations = {
        (
            "Sun",
            "Sun",
            "conjunction",
        ): "A time of renewed vitality and self-expression. Your annual Solar Return brings fresh energy.",
        (
            "Sun",
            "Moon",
            "conjunction",
        ): "Emotions and ego align. A day of emotional clarity and self-awareness.",
        (
            "Moon",
            "Sun",
            "conjunction",
        ): "Heightened emotional sensitivity around your identity and purpose.",
        (
            "Mars",
            "Sun",
            "conjunction",
        ): "High energy and drive. Take action on important matters, but avoid impulsiveness.",
        (
            "Mars",
            "Sun",
            "square",
        ): "Tension and frustration possible. Channel energy constructively.",
        (
            "Jupiter",
            "Sun",
            "conjunction",
        ): "Expansion and opportunity! A fortunate time for growth and optimism.",
        (
            "Jupiter",
            "Sun",
            "trine",
        ): "Smooth sailing. Confidence and luck are on your side.",
        (
            "Saturn",
            "Sun",
            "conjunction",
        ): "A reality check. Time to take responsibility and build lasting structures.",
        (
            "Saturn",
            "Sun",
            "square",
        ): "Obstacles and delays. Patience and perseverance needed.",
        (
            "Venus",
            "Moon",
            "conjunction",
        ): "Emotional warmth and harmony. Good for relationships and self-care.",
        (
            "Venus",
            "Venus",
            "conjunction",
        ): "Your Venus Return! Enhanced attractiveness and relationship focus.",
        (
            "Mercury",
            "Mercury",
            "conjunction",
        ): "Mental clarity. Good for communication and learning.",
    }

    key = (t_planet, n_point, aspect)
    if key in interpretations:
        return interpretations[key]

    # Generic interpretations
    if aspect in ["conjunction", "trine", "sextile"]:
        return f"Harmonious {t_planet} energy activates your natal {n_point}. Positive developments likely."
    else:
        return (
            f"Challenging {t_planet} aspect to your {n_point}. Growth through tension."
        )


def check_daily_transits(profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check today's transits for a profile.

    Returns:
    - date: Today's date
    - transits: List of active transit aspects
    - highlights: Top 3 most significant transits
    - alert_level: low/medium/high based on transit intensity
    """
    now = datetime.now(timezone.utc)

    # Build charts
    natal = build_natal_chart(profile)
    transit = build_transit_chart(profile, now)

    # Find aspects
    aspects = find_transit_aspects(natal, transit)

    # Determine alert level
    tight_aspects = [a for a in aspects if a["orb"] < 1.0]
    challenging = [a for a in aspects if a["aspect"] in ["square", "opposition"]]

    if len(tight_aspects) >= 3 or any(
        a["transit_planet"] in ["Saturn", "Mars"]
        and a["aspect"] in ["square", "opposition"]
        for a in tight_aspects
    ):
        alert_level = "high"
    elif len(tight_aspects) >= 1 or len(challenging) >= 2:
        alert_level = "medium"
    else:
        alert_level = "low"

    # Add interpretations to top aspects
    for asp in aspects[:5]:
        asp["interpretation"] = get_transit_interpretation(asp)

    return {
        "date": now.strftime("%Y-%m-%d"),
        "profile_name": profile.get("name", "Unknown"),
        "transits": aspects,
        "highlights": aspects[:3],
        "total_aspects": len(aspects),
        "alert_level": alert_level,
    }


def find_future_exact_transits(
    profile: Dict[str, Any],
    days_ahead: int = 7,
) -> List[Dict[str, Any]]:
    """
    Find exact future transit-to-natal aspects within the next N days.

    Mirrors the iOS PredictiveScanner behavior closely enough for Android to
    schedule precise local alarms without shipping an ephemeris engine in-app.
    """
    import swisseph as swe

    natal = build_natal_chart(profile)
    natal_planets = {
        planet["name"]: get_absolute_degree(planet["sign"], planet["degree"])
        for planet in natal.get("planets", [])
        if planet.get("name") in NATAL_POINTS
    }

    if not natal_planets:
        return []

    aspect_defs = [
        ("conjunction", 0.0, "major"),
        ("opposition", 180.0, "major"),
        ("trine", 120.0, "major"),
        ("square", 90.0, "major"),
        ("sextile", 60.0, "minor"),
    ]
    transit_planets = [
        (swe.MARS, "Mars"),
        (swe.JUPITER, "Jupiter"),
        (swe.SATURN, "Saturn"),
        (swe.URANUS, "Uranus"),
        (swe.NEPTUNE, "Neptune"),
        (swe.PLUTO, "Pluto"),
    ]

    def julian_day_for(date: datetime) -> float:
        utc_date = date.astimezone(timezone.utc)
        hour = utc_date.hour + utc_date.minute / 60.0 + utc_date.second / 3600.0
        return swe.julday(utc_date.year, utc_date.month, utc_date.day, hour)

    def calculate_positions_at(date: datetime) -> List[Dict[str, Any]]:
        jd = julian_day_for(date)
        positions: List[Dict[str, Any]] = []
        for planet_id, name in transit_planets:
            result, _ = swe.calc_ut(jd, planet_id)
            positions.append(
                {"id": planet_id, "name": name, "degree": result[0] % 360.0}
            )
        return positions

    def normalized_orb(degree1: float, degree2: float, aspect_angle: float) -> float:
        diff = abs(degree1 - degree2)
        if diff > 180:
            diff = 360 - diff
        return abs(diff - aspect_angle)

    def refine_to_exact(
        transit_planet_id: int,
        natal_degree: float,
        aspect_angle: float,
        start_date: datetime,
        hours_range: int = 24,
    ) -> Optional[datetime]:
        best_date = start_date
        best_orb = 999.0

        for hour_offset in range(hours_range):
            check_date = start_date + timedelta(hours=hour_offset)
            result, _ = swe.calc_ut(julian_day_for(check_date), transit_planet_id)
            orb = normalized_orb(result[0] % 360.0, natal_degree, aspect_angle)
            if orb < best_orb:
                best_orb = orb
                best_date = check_date

        minute_start = best_date - timedelta(minutes=30)
        for minute_offset in range(60):
            check_date = minute_start + timedelta(minutes=minute_offset)
            result, _ = swe.calc_ut(julian_day_for(check_date), transit_planet_id)
            orb = normalized_orb(result[0] % 360.0, natal_degree, aspect_angle)
            if orb < best_orb:
                best_orb = orb
                best_date = check_date

        return best_date if best_orb < 1.0 else None

    results: List[Dict[str, Any]] = []
    now = datetime.now(timezone.utc)

    for day_offset in range(days_ahead):
        scan_date = now + timedelta(days=day_offset)
        transit_positions = calculate_positions_at(scan_date)
        for transit in transit_positions:
            for natal_name, natal_degree in natal_planets.items():
                if transit["name"] == natal_name:
                    continue

                for aspect_name, aspect_angle, significance in aspect_defs:
                    orb = normalized_orb(transit["degree"], natal_degree, aspect_angle)
                    if orb > 1.5:
                        continue

                    exact_date = refine_to_exact(
                        transit_planet_id=transit["id"],
                        natal_degree=natal_degree,
                        aspect_angle=aspect_angle,
                        start_date=scan_date,
                    )
                    if exact_date is None:
                        continue

                    is_duplicate = any(
                        existing["transit_planet"] == transit["name"]
                        and existing["natal_point"] == natal_name
                        and existing["aspect"] == aspect_name
                        and abs(
                            datetime.fromisoformat(existing["exact_date"]).timestamp()
                            - exact_date.timestamp()
                        )
                        < 86400
                        for existing in results
                    )
                    if is_duplicate:
                        continue

                    next_day = exact_date + timedelta(days=1)
                    next_day_result, _ = swe.calc_ut(
                        julian_day_for(next_day), transit["id"]
                    )
                    next_day_orb = normalized_orb(
                        next_day_result[0] % 360.0, natal_degree, aspect_angle
                    )

                    results.append(
                        {
                            "transit_planet": transit["name"],
                            "natal_point": natal_name,
                            "aspect": aspect_name,
                            "exact_date": exact_date.isoformat(),
                            "orb": round(orb, 2),
                            "is_applying": next_day_orb > orb,
                            "significance": significance,
                            "interpretation": get_transit_interpretation(
                                {
                                    "transit_planet": transit["name"],
                                    "natal_point": natal_name,
                                    "aspect": aspect_name,
                                }
                            ),
                        }
                    )

    return sorted(results, key=lambda transit: transit["exact_date"])


def format_transit_email(transit_data: Dict[str, Any]) -> tuple[str, str]:
    """
    Format transit data as email subject and HTML body.

    Returns (subject, html_body)
    """
    name = transit_data.get("profile_name", "")
    date = transit_data.get("date", "")
    alert = transit_data.get("alert_level", "low")
    highlights = transit_data.get("highlights", [])

    # Subject
    alert_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(alert, "")
    subject = f"{alert_emoji} Daily Transit Alert for {name} - {date}"

    # HTML body
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, sans-serif; background: #1a1a2e; color: #fff; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; }}
            .header {{ text-align: center; padding: 20px; background: linear-gradient(135deg, #6c5ce7, #4ecdc4); border-radius: 12px; }}
            .transit {{ background: rgba(255,255,255,0.1); padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #4ecdc4; }}
            .transit.challenging {{ border-left-color: #ff6b6b; }}
            .aspect {{ font-size: 18px; font-weight: bold; }}
            .interpretation {{ color: #aaa; font-size: 14px; margin-top: 8px; }}
            .footer {{ text-align: center; color: #888; font-size: 12px; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✨ Daily Transit Alert ✨</h1>
                <p>{name} • {date}</p>
                <p>Alert Level: {alert.upper()} {alert_emoji}</p>
            </div>

            <h2>Today's Highlights</h2>
    """

    for t in highlights:
        is_challenging = t["aspect"] in ["square", "opposition"]
        css_class = "transit challenging" if is_challenging else "transit"
        aspect_symbol = {
            "conjunction": "☌",
            "opposition": "☍",
            "trine": "△",
            "square": "□",
            "sextile": "⚹",
        }.get(t["aspect"], "")

        html += f"""
            <div class="{css_class}">
                <div class="aspect">
                    {t["transit_planet"]} {aspect_symbol} {t["natal_point"]}
                </div>
                <div>
                    {t["aspect"].title()} (orb: {t["orb"]}°)
                </div>
                <div class="interpretation">
                    {t.get("interpretation", "")}
                </div>
            </div>
        """

    html += """
            <div class="footer">
                <p>Powered by AstroNumerology</p>
                <p><a href="#">Manage alert preferences</a></p>
            </div>
        </div>
    </body>
    </html>
    """

    return subject, html


def send_transit_email(
    to_email: str,
    transit_data: Dict[str, Any],
    smtp_config: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Send transit alert email.

    Args:
        to_email: Recipient email address
        transit_data: Transit data from check_daily_transits()
        smtp_config: SMTP configuration dict with host, port, user, password

    Returns:
        True if sent successfully, False otherwise
    """
    if smtp_config is None:
        smtp_config = {
            "host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
            "port": int(os.getenv("SMTP_PORT", "587")),
            "user": os.getenv("SMTP_USER", ""),
            "password": os.getenv("SMTP_PASSWORD", ""),
            "from_email": os.getenv("SMTP_FROM", "alerts@astronumerology.app"),
        }

    if not smtp_config.get("user") or not smtp_config.get("password"):
        logger.warning("SMTP not configured, skipping email")
        return False

    subject, html_body = format_transit_email(transit_data)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_config["from_email"]
    msg["To"] = to_email

    # Plain text fallback
    plain = f"Daily Transit Alert for {transit_data.get('profile_name')}\n"
    plain += f"Date: {transit_data.get('date')}\n"
    plain += f"Alert Level: {transit_data.get('alert_level')}\n\n"
    for t in transit_data.get("highlights", []):
        plain += f"• {t['transit_planet']} {t['aspect']} {t['natal_point']}\n"

    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP(smtp_config["host"], smtp_config["port"]) as server:
            server.starttls()
            server.login(smtp_config["user"], smtp_config["password"])
            server.sendmail(smtp_config["from_email"], to_email, msg.as_string())
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False


def is_mercury_retrograde(jd: float) -> bool:
    """Helper to check if Mercury is retrograde at Julian Day jd."""
    import swisseph as swe

    res, _ = swe.calc_ut(jd, swe.MERCURY)
    return res[3] < 0  # Speed < 0 means retrograde


def check_global_events():
    """Check for major events like retrograde transitions."""
    from datetime import datetime, timezone

    import swisseph as swe

    from .routers.alerts import broadcast_transit_alert

    now = datetime.now(timezone.utc)
    jd = swe.julday(now.year, now.month, now.day, now.hour)

    # Check Mercury Retrograde
    is_retro = is_mercury_retrograde(jd)
    was_retro = is_mercury_retrograde(jd - 1)  # Check yesterday

    if is_retro and not was_retro:
        broadcast_transit_alert(
            "Mercury Retrograde begins! 🌀",
            "Mercury has just turned retrograde. Back up your data and double-check your communications!",
        )
    elif not is_retro and was_retro:
        broadcast_transit_alert(
            "Mercury direct! ✨",
            "Mercury is moving forward again. Time to sign those contracts and move ahead with clarity.",
        )
