"""
numerology_engine.py
--------------------
Computes core numerology numbers and cycles with meaning blocks.
Supports both Pythagorean (default) and Chaldean systems.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from .engine.constants import (
    CHALDEAN_LETTER_VALUES,
    LETTER_VALUES,
    VOWELS,
    reduce_number,
)
from .engine.numerology import calculate_life_path_number_chaldean
from .engine.numerology_extended import (
    _find_karmic_debts,
    calculate_challenges,
    calculate_pinnacles,
)
from .interpretation import NUMEROLOGY_MEANINGS

# Chaldean uses same vowels as Pythagorean for soul urge extraction
_CHALDEAN_VOWELS = VOWELS


_AFFIRMATIONS = {
    1: "I lead with courage and trust my own direction.",
    2: "I create harmony without abandoning my own needs.",
    3: "I let creativity, warmth, and truth move through my voice.",
    4: "I build patiently and give my ideas durable form.",
    5: "I welcome change while staying anchored in what matters.",
    6: "I care deeply and create stability through love and responsibility.",
    7: "I trust reflection, insight, and the wisdom that grows in quiet.",
    8: "I use ambition responsibly and turn effort into tangible results.",
    9: "I serve with compassion and release what has finished its work.",
    11: "I honor intuition and let inspiration become guidance for others.",
    22: "I build big visions with grounded discipline and long-range trust.",
    33: "I teach, heal, and lead with generous love.",
}


def life_path(dob: str, method: str = "pythagorean") -> int:
    """Calculate Life Path by the appropriate method."""
    if method == "chaldean":
        return calculate_life_path_number_chaldean(dob)
    y, m, d = map(int, dob.split("-"))
    month_r = reduce_number(m, keep_master=True)
    day_r = reduce_number(d, keep_master=True)
    year_r = reduce_number(y, keep_master=True)
    return reduce_number(month_r + day_r + year_r)


def _letter_values(method: str) -> dict:
    """Return the correct letter-value table for the given method."""
    return CHALDEAN_LETTER_VALUES if method == "chaldean" else LETTER_VALUES


def expression(name: str, method: str = "pythagorean") -> int:
    lv = _letter_values(method)
    total = sum(lv.get(c, 0) for c in name.lower() if c.isalpha())
    return reduce_number(total)


def _vowels_for_name(name: str) -> set:
    """
    Return the effective vowel set for a name, handling the Y ambiguity.

    Y is treated as a vowel when it acts as the only vowel sound in a position —
    specifically when it is NOT adjacent (left or right) to another standard vowel.
    This matches the most widely-used numerology convention.
    """
    base = set(VOWELS)
    lower = name.lower()
    for i, ch in enumerate(lower):
        if ch == "y":
            left = lower[i - 1] if i > 0 else ""
            right = lower[i + 1] if i < len(lower) - 1 else ""
            # Y is vocalic when not flanked by a standard vowel
            if left not in VOWELS and right not in VOWELS:
                base = base | {"y"}
                break
    return base


def soul_urge(name: str, method: str = "pythagorean") -> int:
    lv = _letter_values(method)
    vowels = _vowels_for_name(name)
    total = sum(lv.get(c, 0) for c in name.lower() if c in vowels)
    return reduce_number(total)


def personality(name: str, method: str = "pythagorean") -> int:
    lv = _letter_values(method)
    total = sum(lv.get(c, 0) for c in name.lower() if c.isalpha() and c not in VOWELS)
    return reduce_number(total)


def birthday_number(dob: str) -> int:
    """Birthday Number: day of birth reduced to single digit or master."""
    d = int(dob.split("-")[2])
    return reduce_number(d)


def personal_year(dob: str, ref: datetime) -> int:
    _, m, d = dob.split("-")
    total = int(m) + int(d) + ref.year
    return reduce_number(total, keep_master=False)


def personal_month(py: int, ref: datetime) -> int:
    return reduce_number(py + ref.month, keep_master=False)


def personal_day(pm: int, ref: datetime) -> int:
    return reduce_number(pm + ref.day, keep_master=False)


def _compact_text(text: str) -> str:
    cleaned = (text or "").strip()
    if not cleaned:
        return ""
    for delimiter in (". ", "! ", "? "):
        if delimiter in cleaned:
            cleaned = cleaned.split(delimiter, 1)[0].strip()
            break
    if cleaned and cleaned[-1] not in ".!?":
        cleaned += "."
    return cleaned


def _sentence_fragment(text: str, fallback: str) -> str:
    fragment = _compact_text(text) or fallback
    fragment = fragment.rstrip(".!?").strip()
    if not fragment:
        return fallback
    return fragment[:1].lower() + fragment[1:]


def _build_dominant_numbers(core: Dict, cycles: Dict) -> List[Dict]:
    return [
        {
            "key": "life_path",
            "label": "Life Path",
            "number": core["life_path"]["number"],
            "meaning": core["life_path"]["meaning"],
        },
        {
            "key": "expression",
            "label": "Expression",
            "number": core["expression"]["number"],
            "meaning": core["expression"]["meaning"],
        },
        {
            "key": "soul_urge",
            "label": "Soul Urge",
            "number": core["soul_urge"]["number"],
            "meaning": core["soul_urge"]["meaning"],
        },
        {
            "key": "personal_year",
            "label": "Personal Year",
            "number": cycles["personal_year"]["number"],
            "meaning": cycles["personal_year"]["meaning"],
        },
    ]


def _build_synthesis(
    core: Dict,
    cycles: Dict,
    karmic_debts: List[Dict],
    pinnacles: List[Dict],
    challenges: List[Dict],
) -> Dict:
    life_path_data = core["life_path"]
    expression_data = core["expression"]
    soul_urge_data = core["soul_urge"]
    personality_data = core["personality"]
    personal_year_data = cycles["personal_year"]
    personal_month_data = cycles["personal_month"]

    strengths = [
        f"Life Path {life_path_data['number']}: {_compact_text(life_path_data['meaning']) or 'Your central direction becomes clearer when you commit to your natural role.'}",
        f"Expression {expression_data['number']}: {_compact_text(expression_data['meaning']) or 'You make the strongest impression when your outer style matches your purpose.'}",
        f"Soul Urge {soul_urge_data['number']}: {_compact_text(soul_urge_data['meaning']) or 'Your inner motivation stays strongest when you honor what genuinely matters to you.'}",
    ]

    growth_edges = [
        f"Personality {personality_data['number']}: {_compact_text(personality_data['meaning']) or 'Watch for the gap between how you appear and what you truly need.'}"
    ]
    if karmic_debts:
        primary_debt = karmic_debts[0]
        growth_edges.append(
            f"{primary_debt.get('label', 'Karmic lesson')}: {_compact_text(primary_debt.get('description', 'A repeating lesson asks for steadier, more conscious choices.'))}"
        )
    elif challenges:
        primary_challenge = challenges[0]
        keyword = primary_challenge.get("keyword") or "Challenge"
        description = _compact_text(
            primary_challenge.get(
                "description", "A recurring lesson is asking for patience and maturity."
            )
        )
        growth_edges.append(f"{keyword}: {description}")

    current_focus = (
        f"Personal Year {personal_year_data['number']} sets the yearly tone through "
        f"{_sentence_fragment(personal_year_data['meaning'], 'measured growth and practical movement')}. "
        f"Personal Month {personal_month_data['number']} refines that timing into "
        f"{_sentence_fragment(personal_month_data['meaning'], 'the next immediate step')} right now."
    )

    if pinnacles:
        current_focus += (
            f" Your longer arc is still shaped by Pinnacle {pinnacles[0].get('number', 0)}, "
            f"which emphasizes {_sentence_fragment(pinnacles[0].get('description', ''), 'long-term development')}"
            f"."
        )

    summary = " ".join(
        [
            f"Life Path {life_path_data['number']} sets the main direction of your numerology, pointing toward {_sentence_fragment(life_path_data['meaning'], 'steady personal development')}.",
            f"Expression {expression_data['number']} and Soul Urge {soul_urge_data['number']} describe how that path moves through both visible style and private desire: {_sentence_fragment(expression_data['meaning'], 'clear self-expression')} paired with {_sentence_fragment(soul_urge_data['meaning'], 'authentic inner motivation')}.",
            current_focus,
        ]
    )

    return {
        "summary": summary,
        "strengths": strengths,
        "growth_edges": growth_edges,
        "current_focus": current_focus,
        "affirmation": _AFFIRMATIONS.get(
            life_path_data["number"],
            "I trust my natural rhythm and meet each lesson with clarity.",
        ),
        "dominant_numbers": _build_dominant_numbers(core, cycles),
    }


def build_numerology(
    name: str, dob: str, ref: datetime, method: str = "pythagorean"
) -> Dict:
    lp = life_path(dob, method)
    expr = expression(name, method)
    soul = soul_urge(name, method)
    persona = personality(name, method)
    bday = birthday_number(dob)
    py = personal_year(dob, ref)
    pm = personal_month(py, ref)
    pd = personal_day(pm, ref)
    meaning_blocks = [
        {"type": "life_path", "value": lp},
        {"type": "expression", "value": expr},
        {"type": "soul_urge", "value": soul},
        {"type": "personality", "value": persona},
        {"type": "birthday", "value": bday},
        {"type": "personal_year", "value": py},
        {"type": "personal_month", "value": pm},
        {"type": "personal_day", "value": pd},
    ]
    core = {
        "life_path": {"number": lp, "meaning": _numerology_text("life_path", lp)},
        "expression": {"number": expr, "meaning": _numerology_text("expression", expr)},
        "soul_urge": {"number": soul, "meaning": _numerology_text("soul_urge", soul)},
        "personality": {
            "number": persona,
            "meaning": _numerology_text("personality", persona),
        },
        "birthday": {"number": bday, "meaning": _numerology_text("birthday", bday)},
    }
    cycles = {
        "personal_year": {
            "number": py,
            "meaning": _numerology_text("personal_year", py),
        },
        "personal_month": {
            "number": pm,
            "meaning": _numerology_text("personal_month", pm),
        },
        "personal_day": {"number": pd, "meaning": _numerology_text("personal_day", pd)},
    }
    karmic_debts = _find_karmic_debts(name, dob)
    pinnacles = calculate_pinnacles(dob)
    challenges = calculate_challenges(dob)
    synthesis = _build_synthesis(core, cycles, karmic_debts, pinnacles, challenges)
    return {
        "core_numbers": core,
        "cycles": cycles,
        "meaning_blocks": meaning_blocks,
        "method": method,
        "pinnacles": pinnacles,
        "challenges": challenges,
        "karmic_debts": karmic_debts,
        "synthesis": synthesis,
    }


def _numerology_text(ntype: str, value: int) -> str:
    key = f"{ntype}_{value}"
    meaning = NUMEROLOGY_MEANINGS.get(key)
    if meaning:
        return meaning["text"]
    base = NUMEROLOGY_MEANINGS.get(ntype, {})
    return base.get("text", "")
