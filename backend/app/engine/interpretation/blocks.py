from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional

# Import the improved text generator from interpretation module
from ...interpretation.planet_sign_meanings import (
    PLANET_ARCHETYPES,
    SIGN_FLAVORS,
    get_planet_sign_text,
)


@dataclass
class MeaningBlock:
    text: str
    tags: List[str] = field(default_factory=list)
    weights: Dict[str, float] = field(default_factory=dict)

    def as_dict(self) -> Dict:
        data = asdict(self)
        data["weights"] = {k: float(v) for k, v in self.weights.items()}
        return data


def get_meaning_block(blocks: Dict, *keys) -> Optional[MeaningBlock]:
    current = blocks
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
        else:
            return None
    return current


def _build_planet_sign_meanings() -> Dict[str, Dict[str, MeaningBlock]]:
    """Generate full planet-sign MeaningBlock dict using improved text."""
    result: Dict[str, Dict[str, MeaningBlock]] = {}
    for planet, pdata in PLANET_ARCHETYPES.items():
        result[planet] = {}
        for sign, sdata in SIGN_FLAVORS.items():
            text = get_planet_sign_text(planet, sign)
            tags = [pdata["focus"], *sdata["tags"]]
            weights = {**pdata["weights"], **sdata["weights"]}
            result[planet][sign] = MeaningBlock(text=text, tags=tags, weights=weights)
    return result


PLANET_SIGN_MEANINGS: Dict[str, Dict[str, MeaningBlock]] = _build_planet_sign_meanings()


PLANET_HOUSE_MEANINGS: Dict[str, Dict[int, MeaningBlock]] = {
    "Sun": {
        1: MeaningBlock(
            text="Identity front-and-center; drives the life direction.",
            tags=["identity", "visibility"],
            weights={"general": 0.7, "career": 0.6},
        ),
        10: MeaningBlock(
            text="Career and reputation are central; ambition is visible.",
            tags=["career", "public"],
            weights={"career": 0.9, "general": 0.6},
        ),
    },
    "Moon": {
        4: MeaningBlock(
            text="Emotional security tied to home and roots.",
            tags=["emotional", "home"],
            weights={"emotional": 0.7, "love": 0.4},
        ),
        7: MeaningBlock(
            text="Feels safe in partnership; intuitively tracks others.",
            tags=["relationship", "empathy"],
            weights={"love": 0.6, "emotional": 0.5},
        ),
    },
    "Venus": {
        5: MeaningBlock(
            text="Romance and pleasure are creative and playful.",
            tags=["love", "creativity", "joy"],
            weights={"love": 0.8, "general": 0.4},
        ),
        7: MeaningBlock(
            text="Partnership focus; values fairness and mutuality.",
            tags=["partnership", "balance"],
            weights={"love": 0.9},
        ),
    },
}


ASPECT_MEANINGS: Dict[str, MeaningBlock] = {
    "conjunction": MeaningBlock(
        text="Two principles fuse powerfully; potential for amplification.",
        tags=["intensity", "focus"],
        weights={"general": 0.6},
    ),
    "square": MeaningBlock(
        text="Dynamic tension that demands action and growth.",
        tags=["challenge", "motivation"],
        weights={"challenge": 0.8},
    ),
    "trine": MeaningBlock(
        text="Natural flow and ease between the planets.",
        tags=["support", "talent"],
        weights={"general": 0.6, "support": 0.8},
    ),
    "opposition": MeaningBlock(
        text="Polarity seeking balance; projection and integration themes.",
        tags=["balance", "relationship"],
        weights={"challenge": 0.6, "love": 0.3},
    ),
    "sextile": MeaningBlock(
        text="Opportunities through cooperation and conscious choice.",
        tags=["opportunity", "support"],
        weights={"support": 0.6},
    ),
}


HOUSE_TOPICS: Dict[int, MeaningBlock] = {
    1: MeaningBlock(text="Identity, body, approach to life", tags=["identity"]),
    2: MeaningBlock(
        text="Resources, money, skills, values", tags=["money", "stability"]
    ),
    5: MeaningBlock(
        text="Romance, creativity, joy, children", tags=["love", "creativity"]
    ),
    6: MeaningBlock(text="Daily work, health, service", tags=["health", "routine"]),
    7: MeaningBlock(
        text="Partnerships, contracts, collaboration", tags=["love", "alliance"]
    ),
    10: MeaningBlock(text="Career, reputation, public life", tags=["career", "status"]),
}


NUMEROLOGY_MEANINGS: Dict[str, MeaningBlock] = {
    "life_path": MeaningBlock(
        text="Core life trajectory and repeating lesson pattern.",
        tags=["purpose"],
        weights={"general": 0.6, "career": 0.5},
    ),
    "expression": MeaningBlock(
        text="How you naturally operate and express talent.",
        tags=["talent"],
        weights={"career": 0.6, "general": 0.4},
    ),
    "soul_urge": MeaningBlock(
        text="Deepest emotional and relational drives.",
        tags=["love", "emotional"],
        weights={"love": 0.6, "emotional": 0.6},
    ),
    "personal_year": MeaningBlock(
        text="Current year tone and opportunities.",
        tags=["timing"],
        weights={"general": 0.4, "career": 0.3, "love": 0.3},
    ),
}
