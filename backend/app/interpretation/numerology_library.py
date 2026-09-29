"""Daily numerology readings from the written library.

A day's reading depends on the Personal Day and Personal Month. Each pairing
has eight passages, one per lens (work, relationships, ...). A person meets
them in order through the calendar year, and a pairing recurs at most eight
times a year, so nobody sees the same passage twice within a year.

Master-number days (11, 22, 33) use the passage for their root day and open
with a line about the master number, drawn from the same lens slot.

The library file is shared with the iOS app, which bundles a copy so Home can
show the same reading offline.
"""

from __future__ import annotations

import json
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional

from ..engine.constants import reduce_number

LIBRARY_PATH = Path(__file__).parent / "library" / "numerology_daily.json"

LENSES = (
    "work",
    "relationships",
    "mind_and_mood",
    "body_and_home",
    "money",
    "creativity",
    "conversations",
    "reflection",
)

MASTER_DAYS = (11, 22, 33)


@lru_cache(maxsize=1)
def load_library() -> Dict:
    return json.loads(LIBRARY_PATH.read_text(encoding="utf-8"))


def _personal_month(personal_year: int, month: int) -> int:
    return reduce_number(personal_year + month, keep_master=True)


def _personal_day(personal_month: int, day: int) -> int:
    return reduce_number(personal_month + day, keep_master=True)


def _root(number: int) -> int:
    return reduce_number(number, keep_master=False)


def lens_slot(personal_year: int, on: date) -> int:
    """Which of the eight versions to show on `on`.

    Counts how many times this day's (day, month) root pairing has already
    come round since 1 January, with the same Personal Year throughout, which
    is how the person's cycle runs.
    """
    pm = _personal_month(personal_year, on.month)
    pairing = (_root(_personal_day(pm, on.day)), _root(pm))

    seen = 0
    for ordinal in range(date(on.year, 1, 1).toordinal(), on.toordinal()):
        earlier = date.fromordinal(ordinal)
        earlier_pm = _personal_month(personal_year, earlier.month)
        if (
            _root(_personal_day(earlier_pm, earlier.day)),
            _root(earlier_pm),
        ) == pairing:
            seen += 1
    return seen % len(LENSES)


def daily_reading(personal_year: int, on: date) -> Optional[Dict]:
    """The written reading for `on`, or None if the library lacks it."""
    library = load_library()
    pm = _personal_month(personal_year, on.month)
    pd = _personal_day(pm, on.day)
    slot = lens_slot(personal_year, on)

    passages = library.get("daily", {}).get(str(_root(pm)), {}).get(str(_root(pd)))
    if not passages or len(passages) != len(LENSES):
        return None

    text = passages[slot]
    if pd in MASTER_DAYS:
        opener = library.get("master_days", {}).get(str(pd), [])
        if len(opener) == len(LENSES):
            text = f"{opener[slot]} {text}"

    return {
        "text": text,
        "lens": LENSES[slot],
        "personal_day": pd,
        "personal_month": pm,
    }


# --- Lifelong, yearly and relationship readings -------------------------

READINGS_PATH = Path(__file__).parent / "library" / "numerology_readings.json"

LIFELONG_POSITIONS = ("life_path", "expression", "soul_urge", "personality", "birthday")

# The order pairs are stored in: master numbers after 9.
_PAIR_ORDER = (1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 22, 33)


@lru_cache(maxsize=1)
def load_readings() -> Dict:
    return json.loads(READINGS_PATH.read_text(encoding="utf-8"))


def lifelong_reading(position: str, number: int) -> Optional[Dict]:
    """{"title", "text"} for a core number in one position, e.g. Life Path 4."""
    return load_readings().get("lifelong", {}).get(position, {}).get(str(number))


def life_path_pair_reading(a: int, b: int) -> Optional[str]:
    """How two Life Paths meet, in either order."""
    if a not in _PAIR_ORDER or b not in _PAIR_ORDER:
        return None
    first, second = sorted((a, b), key=_PAIR_ORDER.index)
    return load_readings().get("compatibility", {}).get(f"{first}-{second}")


def year_reading(life_path: int, personal_year: int) -> Optional[str]:
    """How this Personal Year runs for this Life Path."""
    return (
        load_readings()
        .get("life_path_year", {})
        .get(str(life_path), {})
        .get(str(_root(personal_year)))
    )


def month_reading(personal_year: int, personal_month: int) -> Optional[str]:
    """What this Personal Month adds to the Personal Year."""
    return (
        load_readings()
        .get("month_year", {})
        .get(str(_root(personal_year)), {})
        .get(str(_root(personal_month)))
    )


def cycle_reading(kind: str, number: int) -> Optional[Dict]:
    """Longer text for a pinnacle, challenge or karmic debt number.

    kind is "pinnacles", "challenges" or "karmic_debt"; karmic debt entries
    also carry a title.
    """
    return load_readings().get(kind, {}).get(str(number))
