"""
numerology_engine.py
--------------------
Computes core numerology numbers and cycles with meaning blocks.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict

LETTER_VALUES = {
    **{c: i for i, c in enumerate("abcdefghijklmnopqrstuvwxyz", start=1)},
}

VOWELS = set("aeiouy")


def reduce_num(num: int, keep_master: bool = True) -> int:
    master = {11, 22, 33} if keep_master else set()
    while num > 9 and num not in master:
        num = sum(int(d) for d in str(num))
    return num


def life_path(dob: str) -> int:
    y, m, d = map(int, dob.split("-"))
    return reduce_num(y + m + d)


def expression(name: str) -> int:
    total = sum(LETTER_VALUES.get(c, 0) for c in name.lower() if c.isalpha())
    return reduce_num(total)


def soul_urge(name: str) -> int:
    total = sum(LETTER_VALUES.get(c, 0) for c in name.lower() if c in VOWELS)
    return reduce_num(total)


def personality(name: str) -> int:
    total = sum(
        LETTER_VALUES.get(c, 0) for c in name.lower() if c.isalpha() and c not in VOWELS
    )
    return reduce_num(total)


def personal_year(dob: str, ref: datetime) -> int:
    _, m, d = dob.split("-")
    total = int(m) + int(d) + ref.year
    return reduce_num(total, keep_master=False)


def personal_month(py: int, ref: datetime) -> int:
    return reduce_num(py + ref.month, keep_master=False)


def personal_day(pm: int, ref: datetime) -> int:
    return reduce_num(pm + ref.day, keep_master=False)


def build_numerology(name: str, dob: str, ref: datetime) -> Dict:
    lp = life_path(dob)
    expr = expression(name)
    soul = soul_urge(name)
    persona = personality(name)
    py = personal_year(dob, ref)
    pm = personal_month(py, ref)
    pd = personal_day(pm, ref)
    meaning_blocks = [
        {"type": "life_path", "value": lp},
        {"type": "expression", "value": expr},
        {"type": "soul_urge", "value": soul},
        {"type": "personality", "value": persona},
        {"type": "personal_year", "value": py},
        {"type": "personal_month", "value": pm},
        {"type": "personal_day", "value": pd},
    ]
    return {
        "core_numbers": {
            "life_path": lp,
            "expression": expr,
            "soul_urge": soul,
            "personality": persona,
        },
        "cycles": {"personal_year": py, "personal_month": pm, "personal_day": pd},
        "meaning_blocks": meaning_blocks,
    }
