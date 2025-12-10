"""
numerology_engine.py
--------------------
Computes core numerology numbers and cycles with meaning blocks.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict

from .interpretation import NUMEROLOGY_MEANINGS
from .engine.constants import LETTER_VALUES, VOWELS, reduce_number


def life_path(dob: str) -> int:
    """Calculate Life Path by reducing month, day, year separately then summing."""
    y, m, d = map(int, dob.split("-"))
    # Traditional method: reduce each component first
    month_r = reduce_number(m, keep_master=True)
    day_r = reduce_number(d, keep_master=True)
    year_r = reduce_number(y, keep_master=True)
    return reduce_number(month_r + day_r + year_r)


def expression(name: str) -> int:
    total = sum(LETTER_VALUES.get(c, 0) for c in name.lower() if c.isalpha())
    return reduce_number(total)


def soul_urge(name: str) -> int:
    total = sum(LETTER_VALUES.get(c, 0) for c in name.lower() if c in VOWELS)
    return reduce_number(total)


def personality(name: str) -> int:
    total = sum(
        LETTER_VALUES.get(c, 0) for c in name.lower() if c.isalpha() and c not in VOWELS
    )
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


def build_numerology(name: str, dob: str, ref: datetime) -> Dict:
    lp = life_path(dob)
    expr = expression(name)
    soul = soul_urge(name)
    persona = personality(name)
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
    return {"core_numbers": core, "cycles": cycles, "meaning_blocks": meaning_blocks}


def _numerology_text(ntype: str, value: int) -> str:
    key = f"{ntype}_{value}"
    meaning = NUMEROLOGY_MEANINGS.get(key)
    if meaning:
        return meaning["text"]
    base = NUMEROLOGY_MEANINGS.get(ntype, {})
    return base.get("text", "")
