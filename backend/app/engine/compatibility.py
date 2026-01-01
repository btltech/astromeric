"""Compatibility calculations for astrology and numerology."""

from typing import Dict

from ..interpretation.translations import get_translation
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


def get_element_compat(e1: str, e2: str, lang: str = "en") -> Dict:
    """Get element compatibility data."""
    key = tuple(sorted([e1, e2]))
    if key[0] == key[1]:
        key = (e1, e2)
        
    # Try translation first
    trans_key = f"compat_element_{key[0].lower()}_{key[1].lower()}"
    trans = get_translation(lang, trans_key)
    
    default_data = ELEMENT_COMPAT.get(
        key, {"score": 65, "desc": "Unique combination with growth potential."}
    )
    
    if trans:
        # Assuming translation returns [desc]
        return {"score": default_data["score"], "desc": trans[0]}
        
    return default_data


def get_life_path_compat(lp1: int, lp2: int, lang: str = "en") -> Dict:
    """Get Life Path compatibility data."""
    # Reduce master numbers for lookup
    lp1_r = lp1 if lp1 <= 9 else (lp1 % 10 if lp1 not in [11, 22, 33] else lp1 - 10)
    lp2_r = lp2 if lp2 <= 9 else (lp2 % 10 if lp2 not in [11, 22, 33] else lp2 - 10)

    key = tuple(sorted([lp1_r, lp2_r]))
    if key[0] == key[1]:
        key = (lp1_r, lp2_r)

    default = LIFE_PATH_COMPAT.get(key, {
        "harmony": 70,
        "friction": "Different approaches",
        "advice": "Appreciate your differences.",
    })
    
    if lang != "en":
        friction_key = f"compat_lp_{key[0]}_{key[1]}_friction"
        advice_key = f"compat_lp_{key[0]}_{key[1]}_advice"
        
        friction = get_translation(lang, friction_key)
        advice = get_translation(lang, advice_key)
        
        if friction:
            default = default.copy()
            default["friction"] = friction[0]
        if advice:
            if "friction" not in default: default = default.copy() # Ensure copy if not already
            default["advice"] = advice[0]
            
    return default


def calculate_astro_compatibility(dob1: str, dob2: str, lang: str = "en") -> Dict:
    """Calculate astrology-based compatibility."""
    sign1 = get_zodiac_sign(dob1)
    sign2 = get_zodiac_sign(dob2)
    elem1 = get_element(sign1)
    elem2 = get_element(sign2)

    compat = get_element_compat(elem1, elem2, lang)

    # Localize strengths
    if lang != "en":
        s1_key = "compat_strength_same_element" if elem1 == elem2 else "compat_strength_diff_element"
        s1_trans = get_translation(lang, s1_key)
        s1 = s1_trans[0].format(elem1=elem1, elem2=elem2, element=elem1) if s1_trans else (
            f"Both share {elem1} qualities" if elem1 == elem2 else f"{elem1} and {elem2} can balance each other"
        )
        
        s2_trans = get_translation(lang, "compat_strength_sign1")
        s2 = s2_trans[0].format(sign=sign1) if s2_trans else f"{sign1} brings unique perspective"
        
        s3_trans = get_translation(lang, "compat_strength_sign2")
        s3 = s3_trans[0].format(sign=sign2) if s3_trans else f"{sign2} offers complementary energy"
    else:
        s1 = (
            f"Both share {elem1} qualities"
            if elem1 == elem2
            else f"{elem1} and {elem2} can balance each other"
        )
        s2 = f"{sign1} brings unique perspective"
        s3 = f"{sign2} offers complementary energy"

    return {
        "person1": {"sign": sign1, "element": elem1},
        "person2": {"sign": sign2, "element": elem2},
        "score": compat["score"],
        "element_harmony": compat["desc"],
        "strengths": [s1, s2, s3],
    }


def calculate_numerology_compatibility(
    name1: str, dob1: str, name2: str, dob2: str, lang: str = "en"
) -> Dict:
    """Calculate numerology-based compatibility."""
    lp1 = calculate_life_path_number(dob1)
    lp2 = calculate_life_path_number(dob2)
    expr1 = calculate_expression_number(name1)
    expr2 = calculate_expression_number(name2)
    soul1 = calculate_soul_urge_number(name1)
    soul2 = calculate_soul_urge_number(name2)

    lp_compat = get_life_path_compat(lp1, lp2, lang)

    # Soul Urge compatibility (emotional/heart connection)
    soul_match = 100 - abs(soul1 - soul2) * 10 if soul1 != soul2 else 95

    summary_trans = get_translation(lang, "compat_num_summary")
    summary = summary_trans[0].format(lp1=lp1, lp2=lp2, harmony=lp_compat['harmony']) if summary_trans else f"Life Paths {lp1} and {lp2} create a {lp_compat['harmony']}% harmony match."

    return {
        "person1": {"life_path": lp1, "expression": expr1, "soul_urge": soul1},
        "person2": {"life_path": lp2, "expression": expr2, "soul_urge": soul2},
        "life_path_harmony": lp_compat["harmony"],
        "potential_friction": lp_compat["friction"],
        "advice": lp_compat["advice"],
        "soul_connection": min(100, max(50, soul_match)),
        "summary": summary,
    }


def calculate_combined_compatibility(
    name1: str, dob1: str, name2: str, dob2: str, relationship_type: str = "romantic", lang: str = "en"
) -> Dict:
    """Calculate full combined compatibility report."""
    astro = calculate_astro_compatibility(dob1, dob2, lang)
    numerology = calculate_numerology_compatibility(name1, dob1, name2, dob2, lang)

    # Localize relationship context
    rel_context = RELATIONSHIP_TEXTS.get(
        relationship_type, RELATIONSHIP_TEXTS["romantic"]
    )
    
    frame = rel_context["frame"]
    focus = rel_context["focus"]
    
    if lang != "en":
        frame_trans = get_translation(lang, f"compat_rel_frame_{relationship_type}")
        focus_trans = get_translation(lang, f"compat_rel_focus_{relationship_type}")
        if frame_trans: frame = frame_trans[0]
        if focus_trans: focus = focus_trans[0]

    # Combined score (weighted average)
    combined_score = int(
        astro["score"] * 0.4
        + numerology["life_path_harmony"] * 0.4
        + numerology["soul_connection"] * 0.2
    )

    # Generate advice based on relationship type
    if combined_score >= 85:
        key = "compat_overall_excellent"
        default = f"Excellent {frame}! Natural harmony."
    elif combined_score >= 70:
        key = "compat_overall_strong"
        default = f"Strong {frame} with room to grow."
    elif combined_score >= 55:
        key = "compat_overall_workable"
        default = f"Workable {frame} requiring conscious effort."
    else:
        key = "compat_overall_challenging"
        default = f"Challenging {frame}, but growth potential exists."
        
    overall_trans = get_translation(lang, key)
    overall = overall_trans[0].format(frame=frame) if overall_trans else default

    # Localize top advice
    ta2_trans = get_translation(lang, "compat_advice_leverage")
    ta2 = ta2_trans[0].format(e1=astro['person1']['element'], e2=astro['person2']['element']) if ta2_trans else f"Leverage your {astro['person1']['element']}-{astro['person2']['element']} dynamic"
    
    ta3_trans = get_translation(lang, "compat_advice_communicate")
    ta3 = ta3_trans[0] if ta3_trans else "Communicate openly about differences"

    return {
        "relationship_type": relationship_type,
        "combined_score": combined_score,
        "overall_assessment": overall,
        "astrology": astro,
        "numerology": numerology,
        "focus_areas": focus,
        "top_advice": [
            numerology["advice"],
            ta2,
            ta3,
        ],
    }
