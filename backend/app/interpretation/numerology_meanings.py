"""
numerology_meanings.py
Expanded meaning blocks for numerology types and numbers 1–9.
"""

from __future__ import annotations

from typing import Dict

BASE_TYPES = {
    "life_path": {
        "text": "The road your soul agreed to walk—every twist and lesson circles back to this theme.",
        "tags": ["purpose", "destiny"],
        "weights": {"general": 0.6, "career": 0.5},
    },
    "expression": {
        "text": "The natural broadcast of your gifts—what emerges when you stop editing yourself.",
        "tags": ["talent", "manifestation"],
        "weights": {"career": 0.5, "general": 0.4},
    },
    "soul_urge": {
        "text": "The secret hunger beneath your surface—what your heart whispers when no one's watching.",
        "tags": ["love", "emotional", "desire"],
        "weights": {"love": 0.6, "emotional": 0.5},
    },
    "personality": {
        "text": "The costume you instinctively wear—how the world reads your cover before they open the book.",
        "tags": ["social", "impression"],
        "weights": {"general": 0.3},
    },
    "personal_year": {
        "text": "The cosmic semester you're enrolled in—everything this year teaches rhymes with this vibration.",
        "tags": ["timing", "yearly"],
        "weights": {"general": 0.3, "career": 0.3},
    },
    "personal_month": {
        "text": "The chapter within the chapter—this month's particular flavor and invitation.",
        "tags": ["timing", "monthly"],
        "weights": {"general": 0.2},
    },
    "personal_day": {
        "text": "Today's energetic weather—the note the universe is humming right now.",
        "tags": ["timing", "daily"],
        "weights": {"general": 0.1},
    },
}

NUMBER_TRAITS = {
    1: {
        "phrase": "the spark of new beginnings—pioneer energy that refuses to follow footprints",
        "essence": "You're called to initiate, to go first, to trust your solitary vision.",
        "tags": ["start", "leadership"],
        "weights": {"general": 0.3, "career": 0.3},
    },
    2: {
        "phrase": "the dance of partnership—sensitivity that reads between every line",
        "essence": "Harmony emerges through listening, patience, and the art of the duo.",
        "tags": ["partnership", "receptivity"],
        "weights": {"love": 0.3, "general": 0.2},
    },
    3: {
        "phrase": "the burst of creative expression—words, art, and joy seeking an audience",
        "essence": "Life wants to sparkle through you; let your inner artist play.",
        "tags": ["expression", "creativity"],
        "weights": {"general": 0.3, "career": 0.2},
    },
    4: {
        "phrase": "the architecture of persistence—foundations that outlast their builders",
        "essence": "Brick by patient brick, you construct what others only dream of.",
        "tags": ["structure", "discipline"],
        "weights": {"career": 0.3},
    },
    5: {
        "phrase": "the wild card of freedom—restless evolution refusing to be pinned down",
        "essence": "Change is your oxygen; stagnation is the only real danger.",
        "tags": ["change", "adventure"],
        "weights": {"general": 0.3},
    },
    6: {
        "phrase": "the sanctuary of responsibility—love that shows up through devoted action",
        "essence": "Home, beauty, and care radiate from your presence.",
        "tags": ["care", "nurturing"],
        "weights": {"love": 0.3, "general": 0.2},
    },
    7: {
        "phrase": "the deep dive of the seeker—truth found in solitude and sacred questions",
        "essence": "Your mind is a temple; wisdom arrives when you trust the quiet.",
        "tags": ["insight", "spirituality"],
        "weights": {"spiritual": 0.3, "general": 0.2},
    },
    8: {
        "phrase": "the circuit of power and manifestation—material mastery earned through effort",
        "essence": "You understand that abundance and ambition are spiritual practices.",
        "tags": ["power", "abundance"],
        "weights": {"career": 0.3},
    },
    9: {
        "phrase": "the completion that opens doors—wisdom gathered and released for others",
        "essence": "You're here to synthesize, heal, and let endings birth something universal.",
        "tags": ["closure", "compassion"],
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
        # Evocative text that captures the unique vibration
        text = f"Resonates with {ndata['phrase']}. {ndata['essence']}"
        tags = tdata["tags"] + ndata["tags"]
        weights = _merge_weights(tdata["weights"], ndata["weights"])
        NUMEROLOGY_MEANINGS[key] = {"text": text, "tags": tags, "weights": weights}
