"""
compatibility.py
Builds a compatibility report using Pro-Level synastry and numerology between two profiles.
Uses the 6-dimension weighted scoring system (Moon, Venus, Modality, Element, Life Path, Soul Urge).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from ..engine.compatibility import calculate_combined_compatibility


def build_compatibility(
    person_a: Dict, person_b: Dict, lang: str = "en"
) -> Dict[str, Any]:
    """
    Build a full compatibility report using Pro-Level engine.

    Returns a structure matching the v2 API CompatibilityData schema:
    - overall_score: 0.0-1.0 normalized score
    - summary: Overall assessment text
    - dimensions: List of scored compatibility dimensions
    - strengths: Relationship strengths
    - challenges: Potential friction areas
    - recommendations: Actionable advice
    """
    # Use the Pro-Level combined compatibility engine
    result = calculate_combined_compatibility(
        name1=person_a["name"],
        dob1=person_a["date_of_birth"],
        name2=person_b["name"],
        dob2=person_b["date_of_birth"],
        relationship_type="romantic",
        lang=lang,
    )

    # Transform engine output to API response format
    score_breakdown = result.get("score_breakdown", {})

    # Build dimensions array from score breakdown
    dimensions = _build_dimensions(score_breakdown, result)

    # Extract strengths from astrology data
    astro = result.get("astrology", {})
    strengths = astro.get("strengths", [])

    # Build challenges from numerology friction
    numerology = result.get("numerology", {})
    challenges = []
    if numerology.get("potential_friction"):
        challenges.append(numerology["potential_friction"])

    # Build recommendations from top_advice
    recommendations = result.get("top_advice", [])
    if isinstance(recommendations, str):
        recommendations = [recommendations]

    return {
        "overall_score": float(result.get("combined_score", 70)),  # 0-100 scale
        "summary": result.get("overall_assessment", ""),
        "dimensions": dimensions,
        "strengths": strengths[:5] if strengths else _default_strengths(astro),
        "challenges": challenges[:3] if challenges else [],
        "recommendations": recommendations[:3],
        # Include detailed breakdown for advanced views
        "score_breakdown": score_breakdown,
        "astrology": astro,
        "numerology": numerology,
    }


def _build_dimensions(score_breakdown: Dict, result: Dict) -> List[Dict[str, Any]]:
    """Transform score_breakdown into CompatibilityScore dimensions."""
    dimensions = []

    # Element Harmony (20%)
    element = score_breakdown.get("element_harmony", {})
    if element:
        dimensions.append(
            {
                "name": "Element Harmony",
                "score": float(element.get("score", 70)),  # 0-100 scale
                "interpretation": element.get("desc", ""),
            }
        )

    # Modality Match (15%)
    modality = score_breakdown.get("modality_match", {})
    if modality:
        dimensions.append(
            {
                "name": "Modality Match",
                "score": float(modality.get("score", 70)),  # 0-100 scale
                "interpretation": modality.get("desc", ""),
            }
        )

    # Moon Connection (20%)
    moon = score_breakdown.get("moon_connection", {})
    if moon:
        moon_desc = moon.get("desc", "")
        moon1 = moon.get("moon1", "")
        moon2 = moon.get("moon2", "")
        if moon1 and moon2 and not moon_desc:
            moon_desc = f"Moon in {moon1} & {moon2}"
        dimensions.append(
            {
                "name": "Emotional Connection",
                "score": float(moon.get("score", 70)),  # 0-100 scale
                "interpretation": moon_desc,
            }
        )

    # Venus Harmony (15%)
    venus = score_breakdown.get("venus_harmony", {})
    if venus:
        venus_desc = venus.get("desc", "")
        venus1 = venus.get("venus1", "")
        venus2 = venus.get("venus2", "")
        if venus1 and venus2 and not venus_desc:
            venus_desc = f"Venus in {venus1} & {venus2}"
        dimensions.append(
            {
                "name": "Love Style",
                "score": float(venus.get("score", 70)),  # 0-100 scale
                "interpretation": venus_desc,
            }
        )

    # Life Path (20%)
    life_path = score_breakdown.get("life_path", {})
    numerology = result.get("numerology", {})
    if life_path or numerology:
        lp_score = life_path.get("score", numerology.get("life_path_harmony", 70))
        lp1 = numerology.get("person1", {}).get("life_path", 0)
        lp2 = numerology.get("person2", {}).get("life_path", 0)
        dimensions.append(
            {
                "name": "Life Path",
                "score": float(lp_score),  # 0-100 scale
                "interpretation": f"Life Paths {lp1} and {lp2} - {numerology.get('advice', '')}",
            }
        )

    # Soul Urge (10%)
    soul = score_breakdown.get("soul_urge", {})
    if soul or numerology:
        soul_score = soul.get("score", numerology.get("soul_connection", 70))
        dimensions.append(
            {
                "name": "Soul Connection",
                "score": float(soul_score),  # 0-100 scale
                "interpretation": numerology.get(
                    "summary", "Deep inner connection potential."
                ),
            }
        )

    return dimensions


def _default_strengths(astro: Dict) -> List[str]:
    """Generate default strengths from astrology data."""
    strengths = []
    p1 = astro.get("person1", {})
    p2 = astro.get("person2", {})

    if p1.get("element") and p2.get("element"):
        if p1["element"] == p2["element"]:
            strengths.append(
                f"Both share {p1['element']} energy - natural understanding"
            )
        else:
            strengths.append(
                f"{p1['element']} and {p2['element']} create balanced dynamic"
            )

    if p1.get("sign") and p2.get("sign"):
        strengths.append(
            f"{p1['sign']} brings initiative, {p2['sign']} offers stability"
        )

    return strengths
