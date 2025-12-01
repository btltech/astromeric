"""
pdf_service.py
--------------
Generate PDF natal chart reports using reportlab.
"""
from __future__ import annotations

import io
from datetime import datetime
from typing import Any, Dict, Optional

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


ZODIAC_SYMBOLS = {
    "Aries": "♈",
    "Taurus": "♉",
    "Gemini": "♊",
    "Cancer": "♋",
    "Leo": "♌",
    "Virgo": "♍",
    "Libra": "♎",
    "Scorpio": "♏",
    "Sagittarius": "♐",
    "Capricorn": "♑",
    "Aquarius": "♒",
    "Pisces": "♓",
}

PLANET_SYMBOLS = {
    "Sun": "☉",
    "Moon": "☽",
    "Mercury": "☿",
    "Venus": "♀",
    "Mars": "♂",
    "Jupiter": "♃",
    "Saturn": "♄",
    "Uranus": "♅",
    "Neptune": "♆",
    "Pluto": "♇",
}


def generate_natal_pdf(
    profile: Dict[str, Any],
    natal_data: Dict[str, Any],
    numerology_data: Optional[Dict[str, Any]] = None,
) -> bytes:
    """
    Generate a PDF natal chart report.

    Args:
        profile: User profile with name, date_of_birth, etc.
        natal_data: Natal chart data with planets, houses, aspects
        numerology_data: Optional numerology profile data

    Returns:
        PDF file as bytes
    """
    if not HAS_REPORTLAB:
        raise ImportError(
            "reportlab is required for PDF generation. Install with: pip install reportlab"
        )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        spaceAfter=20,
        textColor=colors.HexColor("#4ecdc4"),
        alignment=1,  # Center
    )
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=16,
        spaceBefore=15,
        spaceAfter=10,
        textColor=colors.HexColor("#6c5ce7"),
    )
    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["Normal"],
        fontSize=11,
        spaceAfter=8,
        leading=14,
    )
    small_style = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.gray,
    )

    elements = []

    # Title
    elements.append(Paragraph("✨ Natal Chart Report ✨", title_style))
    elements.append(Spacer(1, 10))

    # Profile info
    name = profile.get("name", "Unknown")
    dob = profile.get("date_of_birth", "")
    tob = profile.get("time_of_birth", "Unknown")
    place = profile.get("place_of_birth", "")

    elements.append(
        Paragraph(
            f"<b>{name}</b>",
            ParagraphStyle("Name", parent=body_style, fontSize=14, alignment=1),
        )
    )
    elements.append(
        Paragraph(
            f"Born: {dob} at {tob}<br/>{place}",
            ParagraphStyle("BirthInfo", parent=small_style, alignment=1),
        )
    )
    elements.append(Spacer(1, 20))

    # Sun, Moon, Rising
    chart = natal_data.get("chart", {})
    planets_list = chart.get("planets", [])
    planets_dict = {p["name"]: p for p in planets_list}

    houses_list = chart.get("houses", [])
    ascendant = next((h for h in houses_list if h["house"] == 1), {})

    sun = planets_dict.get("Sun", {})
    moon = planets_dict.get("Moon", {})

    summary_data = [
        ["☉ Sun Sign", f"{sun.get('sign', 'N/A')} {sun.get('degree', 0):.1f}°"],
        ["☽ Moon Sign", f"{moon.get('sign', 'N/A')} {moon.get('degree', 0):.1f}°"],
        [
            "↑ Rising Sign",
            f"{ascendant.get('sign', 'N/A')} {ascendant.get('degree', 0):.1f}°",
        ],
    ]

    summary_table = Table(summary_data, colWidths=[2.5 * inch, 3 * inch])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#1a1a2e")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTSIZE", (0, 0), (-1, -1), 12),
                ("PADDING", (0, 0), (-1, -1), 12),
                ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#3d3d5c")),
            ]
        )
    )
    elements.append(summary_table)
    elements.append(Spacer(1, 20))

    # Planet Positions
    elements.append(Paragraph("🪐 Planet Positions", heading_style))

    planet_data = [["Planet", "Sign", "Degree", "House"]]
    for planet_name in [
        "Sun",
        "Moon",
        "Mercury",
        "Venus",
        "Mars",
        "Jupiter",
        "Saturn",
        "Uranus",
        "Neptune",
        "Pluto",
    ]:
        p = planets_dict.get(planet_name, {})
        if p:
            symbol = PLANET_SYMBOLS.get(planet_name, "")
            sign_symbol = ZODIAC_SYMBOLS.get(p.get("sign", ""), "")
            planet_data.append(
                [
                    f"{symbol} {planet_name}",
                    f"{sign_symbol} {p.get('sign', 'N/A')}",
                    f"{p.get('degree', 0):.2f}°",
                    str(p.get("house", "N/A")),
                ]
            )

    planet_table = Table(
        planet_data, colWidths=[1.8 * inch, 1.8 * inch, 1.2 * inch, 1 * inch]
    )
    planet_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#6c5ce7")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("PADDING", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#3d3d5c")),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.HexColor("#f8f9fa"), colors.white],
                ),
            ]
        )
    )
    elements.append(planet_table)
    elements.append(Spacer(1, 20))

    # Aspects
    aspects = chart.get("aspects", [])
    if aspects:
        elements.append(Paragraph("⚛️ Major Aspects", heading_style))

        aspect_data = [["Aspect", "Orb"]]
        for asp in aspects[:12]:  # Limit to top 12
            aspect_data.append(
                [
                    f"{asp.get('planet1', '')} {asp.get('aspect', '')} {asp.get('planet2', '')}",
                    f"{asp.get('orb', 0):.1f}°",
                ]
            )

        aspect_table = Table(aspect_data, colWidths=[4 * inch, 1.5 * inch])
        aspect_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e17055")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("PADDING", (0, 0), (-1, -1), 6),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#ddd")),
                ]
            )
        )
        elements.append(aspect_table)
        elements.append(Spacer(1, 20))

    # Numerology Section
    if numerology_data:
        elements.append(Paragraph("🔢 Numerology Profile", heading_style))

        life_path = numerology_data.get("life_path", {})
        expression = numerology_data.get("expression", {})
        soul_urge = numerology_data.get("soul_urge", {})

        num_data = [
            ["Number", "Value", "Meaning"],
            [
                "Life Path",
                str(life_path.get("number", "")),
                life_path.get("meaning", "")[:50] + "...",
            ],
            [
                "Expression",
                str(expression.get("number", "")),
                expression.get("meaning", "")[:50] + "...",
            ],
            [
                "Soul Urge",
                str(soul_urge.get("number", "")),
                soul_urge.get("meaning", "")[:50] + "...",
            ],
        ]

        num_table = Table(num_data, colWidths=[1.5 * inch, 0.8 * inch, 3.5 * inch])
        num_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4ecdc4")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ALIGN", (0, 0), (1, -1), "CENTER"),
                    ("ALIGN", (2, 0), (2, -1), "LEFT"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("PADDING", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#ddd")),
                ]
            )
        )
        elements.append(num_table)
        elements.append(Spacer(1, 20))

    # Interpretations
    interpretations = natal_data.get("interpretations", [])
    if interpretations:
        elements.append(Paragraph("📖 Interpretations", heading_style))

        for interp in interpretations[:5]:  # Limit
            title = interp.get("title", "")
            text = interp.get("text", "")[:300]
            elements.append(Paragraph(f"<b>{title}</b>", body_style))
            elements.append(Paragraph(text, small_style))
            elements.append(Spacer(1, 10))

    # Footer
    elements.append(Spacer(1, 30))
    elements.append(
        Paragraph(
            f"Generated by AstroNumerology • {datetime.now().strftime('%B %d, %Y')}",
            ParagraphStyle("Footer", parent=small_style, alignment=1),
        )
    )

    doc.build(elements)
    return buffer.getvalue()


def generate_compatibility_pdf(
    person_a: Dict[str, Any],
    person_b: Dict[str, Any],
    compatibility_data: Dict[str, Any],
) -> bytes:
    """Generate a PDF compatibility report for two people."""
    if not HAS_REPORTLAB:
        raise ImportError("reportlab required")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    elements = []

    # Title
    elements.append(
        Paragraph(
            "💕 Compatibility Report 💕",
            ParagraphStyle(
                "Title",
                parent=styles["Title"],
                alignment=1,
                textColor=colors.HexColor("#fd79a8"),
            ),
        )
    )
    elements.append(Spacer(1, 20))

    # Names
    elements.append(
        Paragraph(
            f"<b>{person_a.get('name', 'Person A')}</b> &amp; <b>{person_b.get('name', 'Person B')}</b>",
            ParagraphStyle("Names", parent=styles["Heading2"], alignment=1),
        )
    )
    elements.append(Spacer(1, 20))

    # Overall score
    score = compatibility_data.get("overall_score")
    if score is None:
        topic_scores = compatibility_data.get("topic_scores", {})
        if topic_scores:
            avg = sum(topic_scores.values()) / len(topic_scores)
            score = int(avg * 10)
        else:
            score = 0

    elements.append(
        Paragraph(
            f"Overall Compatibility: <b>{score}%</b>",
            ParagraphStyle(
                "Score",
                parent=styles["Heading1"],
                alignment=1,
                textColor=colors.HexColor("#4ecdc4")
                if score >= 70
                else colors.HexColor("#e17055"),
            ),
        )
    )
    elements.append(Spacer(1, 20))

    # Strengths
    strengths = compatibility_data.get("strengths", [])
    if strengths:
        elements.append(Paragraph("✨ Strengths", styles["Heading2"]))
        for s in strengths:
            elements.append(Paragraph(f"• {s}", styles["Normal"]))
        elements.append(Spacer(1, 15))

    # Challenges
    challenges = compatibility_data.get("challenges", [])
    if challenges:
        elements.append(Paragraph("⚡ Challenges", styles["Heading2"]))
        for c in challenges:
            elements.append(Paragraph(f"• {c}", styles["Normal"]))
        elements.append(Spacer(1, 15))

    # Advice
    advice = compatibility_data.get("advice", "")
    if advice:
        elements.append(Paragraph("💡 Advice", styles["Heading2"]))
        elements.append(Paragraph(advice, styles["Normal"]))

    doc.build(elements)
    return buffer.getvalue()
