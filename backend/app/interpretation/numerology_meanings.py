"""
numerology_meanings.py
Expanded meaning blocks for numerology types and numbers 1–9.
"""

from __future__ import annotations

from typing import Dict

BASE_TYPES = {
    "life_path": {
        "text": "Core trajectory and repeated lessons.",
        "tags": ["purpose"],
        "weights": {"general": 0.6, "career": 0.5},
    },
    "expression": {
        "text": "How talents express outwardly.",
        "tags": ["talent"],
        "weights": {"career": 0.5, "general": 0.4},
    },
    "soul_urge": {
        "text": "Deepest heart desires and attraction style.",
        "tags": ["love", "emotional"],
        "weights": {"love": 0.6, "emotional": 0.5},
    },
    "personality": {
        "text": "Outer mask and first impression.",
        "tags": ["social"],
        "weights": {"general": 0.3},
    },
    "personal_year": {
        "text": "Theme of the year—macro timing.",
        "tags": ["timing"],
        "weights": {"general": 0.3, "career": 0.3},
    },
    "personal_month": {
        "text": "Month flavor—micro timing.",
        "tags": ["timing"],
        "weights": {"general": 0.2},
    },
    "personal_day": {
        "text": "Day tone—fine timing.",
        "tags": ["timing"],
        "weights": {"general": 0.1},
    },
}

NUMBER_TRAITS = {
    1: {
        "phrase": "initiation and independence",
        "tags": ["start"],
        "weights": {"general": 0.3, "career": 0.3},
    },
    2: {
        "phrase": "cooperation and diplomacy",
        "tags": ["partnership"],
        "weights": {"love": 0.3, "general": 0.2},
    },
    3: {
        "phrase": "expression and creativity",
        "tags": ["expression"],
        "weights": {"general": 0.3, "career": 0.2},
    },
    4: {
        "phrase": "structure and steady building",
        "tags": ["structure"],
        "weights": {"career": 0.3},
    },
    5: {
        "phrase": "change and adaptability",
        "tags": ["change"],
        "weights": {"general": 0.3},
    },
    6: {
        "phrase": "care and responsibility",
        "tags": ["care"],
        "weights": {"love": 0.3, "general": 0.2},
    },
    7: {
        "phrase": "insight and reflection",
        "tags": ["insight"],
        "weights": {"spiritual": 0.3, "general": 0.2},
    },
    8: {
        "phrase": "power and material mastery",
        "tags": ["power"],
        "weights": {"career": 0.3},
    },
    9: {
        "phrase": "completion and compassion",
        "tags": ["closure"],
        "weights": {"spiritual": 0.3, "emotional": 0.2},
    },
}


def _merge_weights(base: Dict[str, float], extra: Dict[str, float]) -> Dict[str, float]:
    weights = base.copy()
    for key, val in extra.items():
        weights[key] = round(weights.get(key, 0.0) + val, 2)
    return weights


NUMEROLOGY_MEANINGS: Dict[str, Dict] = {}
NUMEROLOGY_MEANINGS.update(BASE_TYPES)

for tkey, tdata in BASE_TYPES.items():
    for number, ndata in NUMBER_TRAITS.items():
        key = f"{tkey}_{number}"
        text = (
            f"{tkey.replace('_', ' ').title()} {number}: emphasizes {ndata['phrase']}."
        )
        tags = tdata["tags"] + ndata["tags"]
        weights = _merge_weights(tdata["weights"], ndata["weights"])
        NUMEROLOGY_MEANINGS[key] = {"text": text, "tags": tags, "weights": weights}
