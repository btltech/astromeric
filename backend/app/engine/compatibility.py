"""Compatibility calculations for astrology and numerology."""

from typing import Dict

from .astrology import get_element, get_zodiac_sign
from .numerology import calculate_life_path_number
from .numerology_extended import calculate_expression_number, calculate_soul_urge_number

# Element compatibility matrix
ELEMENT_COMPAT = {
    ("Fire", "Fire"): {
        "score": 80,
        "desc": "Passionate and dynamic, but watch for power struggles.",
    },
    ("Fire", "Air"): {
        "score": 90,
        "desc": "Exciting combination! Air fans Fire's flames.",
    },
    ("Fire", "Earth"): {
        "score": 50,
        "desc": "Different paces. Fire inspires, Earth grounds.",
    },
    ("Fire", "Water"): {
        "score": 40,
        "desc": "Steam or sizzle? Emotional intensity ahead.",
    },
    ("Air", "Air"): {
        "score": 75,
        "desc": "Intellectual connection, but may lack grounding.",
    },
    ("Air", "Earth"): {
        "score": 55,
        "desc": "Head vs. heart. Needs patience and compromise.",
    },
    ("Air", "Water"): {
        "score": 60,
        "desc": "Creative potential if emotions are honored.",
    },
    ("Earth", "Earth"): {
        "score": 85,
        "desc": "Stable and reliable. Build something lasting.",
    },
    ("Earth", "Water"): {
        "score": 90,
        "desc": "Nurturing and supportive. Natural harmony.",
    },
    ("Water", "Water"): {
        "score": 80,
        "desc": "Deep emotional bond. Watch for overwhelm.",
    },
}

# Life Path compatibility
LIFE_PATH_COMPAT = {
    (1, 1): {
        "harmony": 70,
        "friction": "Power struggles",
        "advice": "Take turns leading.",
    },
    (1, 2): {
        "harmony": 85,
        "friction": "Independence vs. togetherness",
        "advice": "Balance autonomy with partnership.",
    },
    (1, 3): {
        "harmony": 90,
        "friction": "Focus differences",
        "advice": "Combine leadership with creativity.",
    },
    (1, 5): {
        "harmony": 95,
        "friction": "Restlessness",
        "advice": "Adventure together.",
    },
    (2, 2): {
        "harmony": 85,
        "friction": "Over-sensitivity",
        "advice": "Communicate feelings openly.",
    },
    (2, 6): {
        "harmony": 95,
        "friction": "Dependency",
        "advice": "Nurture each other equally.",
    },
    (3, 3): {
        "harmony": 80,
        "friction": "Scattered energy",
        "advice": "Focus your creative powers.",
    },
    (3, 5): {
        "harmony": 90,
        "friction": "Commitment fears",
        "advice": "Keep things exciting but stable.",
    },
    (4, 4): {
        "harmony": 80,
        "friction": "Rigidity",
        "advice": "Allow flexibility in routines.",
    },
    (4, 8): {
        "harmony": 95,
        "friction": "Workaholism",
        "advice": "Build empire, but make time for each other.",
    },
    (5, 5): {
        "harmony": 85,
        "friction": "Lack of stability",
        "advice": "Create some grounding rituals.",
    },
    (6, 6): {"harmony": 90, "friction": "Over-giving", "advice": "Remember self-care."},
    (7, 7): {
        "harmony": 85,
        "friction": "Isolation",
        "advice": "Share your inner worlds.",
    },
    (8, 8): {
        "harmony": 80,
        "friction": "Competition",
        "advice": "Collaborate, don't compete.",
    },
    (9, 9): {
        "harmony": 90,
        "friction": "Idealism",
        "advice": "Ground your visions in reality.",
    },
}

RELATIONSHIP_TEXTS = {
    "romantic": {
        "frame": "romantic partnership",
        "focus": "love, intimacy, long-term potential",
    },
    "friend": {"frame": "friendship", "focus": "trust, fun, mutual support"},
    "family": {
        "frame": "family bond",
        "focus": "understanding, acceptance, shared history",
    },
    "business": {
        "frame": "business partnership",
        "focus": "collaboration, strengths, professional synergy",
    },
}


def get_element_compat(e1: str, e2: str) -> Dict:
    """Get element compatibility data."""
    key = tuple(sorted([e1, e2]))
    if key[0] == key[1]:
        key = (e1, e2)
    return ELEMENT_COMPAT.get(
        key, {"score": 65, "desc": "Unique combination with growth potential."}
    )


def get_life_path_compat(lp1: int, lp2: int) -> Dict:
    """Get Life Path compatibility data."""
    # Reduce master numbers for lookup
    lp1_r = lp1 if lp1 <= 9 else (lp1 % 10 if lp1 not in [11, 22, 33] else lp1 - 10)
    lp2_r = lp2 if lp2 <= 9 else (lp2 % 10 if lp2 not in [11, 22, 33] else lp2 - 10)

    key = tuple(sorted([lp1_r, lp2_r]))
    if key[0] == key[1]:
        key = (lp1_r, lp2_r)

    default = {
        "harmony": 70,
        "friction": "Different approaches",
        "advice": "Appreciate your differences.",
    }
    return LIFE_PATH_COMPAT.get(key, default)


def calculate_astro_compatibility(dob1: str, dob2: str) -> Dict:
    """Calculate astrology-based compatibility."""
    sign1 = get_zodiac_sign(dob1)
    sign2 = get_zodiac_sign(dob2)
    elem1 = get_element(sign1)
    elem2 = get_element(sign2)

    compat = get_element_compat(elem1, elem2)

    return {
        "person1": {"sign": sign1, "element": elem1},
        "person2": {"sign": sign2, "element": elem2},
        "score": compat["score"],
        "element_harmony": compat["desc"],
        "strengths": [
            (
                f"Both share {elem1} qualities"
                if elem1 == elem2
                else f"{elem1} and {elem2} can balance each other"
            ),
            f"{sign1} brings unique perspective",
            f"{sign2} offers complementary energy",
        ],
    }


def calculate_numerology_compatibility(
    name1: str, dob1: str, name2: str, dob2: str
) -> Dict:
    """Calculate numerology-based compatibility."""
    lp1 = calculate_life_path_number(dob1)
    lp2 = calculate_life_path_number(dob2)
    expr1 = calculate_expression_number(name1)
    expr2 = calculate_expression_number(name2)
    soul1 = calculate_soul_urge_number(name1)
    soul2 = calculate_soul_urge_number(name2)

    lp_compat = get_life_path_compat(lp1, lp2)

    # Soul Urge compatibility (emotional/heart connection)
    soul_match = 100 - abs(soul1 - soul2) * 10 if soul1 != soul2 else 95

    return {
        "person1": {"life_path": lp1, "expression": expr1, "soul_urge": soul1},
        "person2": {"life_path": lp2, "expression": expr2, "soul_urge": soul2},
        "life_path_harmony": lp_compat["harmony"],
        "potential_friction": lp_compat["friction"],
        "advice": lp_compat["advice"],
        "soul_connection": min(100, max(50, soul_match)),
        "summary": f"Life Paths {lp1} and {lp2} create a {lp_compat['harmony']}% harmony match.",
    }


def calculate_combined_compatibility(
    name1: str, dob1: str, name2: str, dob2: str, relationship_type: str = "romantic"
) -> Dict:
    """Calculate full combined compatibility report."""
    astro = calculate_astro_compatibility(dob1, dob2)
    numerology = calculate_numerology_compatibility(name1, dob1, name2, dob2)

    rel_context = RELATIONSHIP_TEXTS.get(
        relationship_type, RELATIONSHIP_TEXTS["romantic"]
    )

    # Combined score (weighted average)
    combined_score = int(
        astro["score"] * 0.4
        + numerology["life_path_harmony"] * 0.4
        + numerology["soul_connection"] * 0.2
    )

    # Generate advice based on relationship type
    if combined_score >= 85:
        overall = f"Excellent {rel_context['frame']}! Natural harmony."
    elif combined_score >= 70:
        overall = f"Strong {rel_context['frame']} with room to grow."
    elif combined_score >= 55:
        overall = f"Workable {rel_context['frame']} requiring conscious effort."
    else:
        overall = f"Challenging {rel_context['frame']}, but growth potential exists."

    return {
        "relationship_type": relationship_type,
        "combined_score": combined_score,
        "overall_assessment": overall,
        "astrology": astro,
        "numerology": numerology,
        "focus_areas": rel_context["focus"],
        "top_advice": [
            numerology["advice"],
            f"Leverage your {astro['person1']['element']}-{astro['person2']['element']} dynamic",
            "Communicate openly about differences",
        ],
    }
