from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional

from ..charts.models import Aspect, Chart, PlanetPosition
from ..interpretation import (
    ASPECT_MEANINGS,
    HOUSE_TOPICS,
    NUMEROLOGY_MEANINGS,
    PLANET_HOUSE_MEANINGS,
    PLANET_SIGN_MEANINGS,
    MeaningBlock,
    get_meaning_block,
)


@dataclass
class Factor:
    code: str
    label: str
    score: float
    topic_scores: Dict[str, float] = field(default_factory=dict)
    meaning: Optional[MeaningBlock] = None
    context: Dict[str, str] = field(default_factory=dict)

    def as_dict(self) -> Dict:
        data = asdict(self)
        if self.meaning:
            data["meaning"] = self.meaning.as_dict()
        return data


@dataclass
class RuleResult:
    topic_scores: Dict[str, float]
    factors: List[Factor]

    def as_dict(self) -> Dict:
        return {
            "topic_scores": self.topic_scores,
            "factors": [f.as_dict() for f in self.factors],
        }


class RuleEngine:
    """Generic scoring engine that can operate on any chart type."""

    def __init__(self, base_weights: Optional[Dict[str, float]] = None):
        self.base_weights = base_weights or {
            "love": 1.0,
            "career": 1.0,
            "emotional": 1.0,
            "general": 1.0,
            "challenge": 1.0,
            "support": 1.0,
            "health": 1.0,
        }

    def evaluate(
        self,
        query_type: str,
        chart: Chart,
        transit_aspects: Optional[List[Aspect]] = None,
        synastry_aspects: Optional[List[Aspect]] = None,
        numerology: Optional[Dict] = None,
    ) -> RuleResult:
        factors: List[Factor] = []
        factors.extend(self._natal_sign_factors(chart, query_type))
        factors.extend(self._natal_house_factors(chart, query_type))
        factors.extend(self._aspect_factors(chart.aspects, "natal"))

        if transit_aspects:
            factors.extend(self._aspect_factors(transit_aspects, "transit"))
        if synastry_aspects:
            factors.extend(self._aspect_factors(synastry_aspects, "synastry"))
        if numerology:
            factors.extend(self._numerology_factors(numerology))

        topic_scores = self._aggregate_scores(factors)
        return RuleResult(topic_scores=topic_scores, factors=factors)

    def _natal_sign_factors(self, chart: Chart, query_type: str) -> List[Factor]:
        factors: List[Factor] = []
        for planet in chart.planets:
            meaning = get_meaning_block(PLANET_SIGN_MEANINGS, planet.name, planet.sign)
            if meaning:
                score = self._base_score(meaning.weights, query_type)
                factors.append(
                    Factor(
                        code=f"{planet.name}_in_{planet.sign}",
                        label=f"{planet.name} in {planet.sign}",
                        score=score,
                        topic_scores=meaning.weights,
                        meaning=meaning,
                        context={"kind": "planet_sign"},
                    )
                )
        return factors

    def _natal_house_factors(self, chart: Chart, query_type: str) -> List[Factor]:
        factors: List[Factor] = []
        for planet in chart.planets:
            if planet.house:
                meaning = get_meaning_block(PLANET_HOUSE_MEANINGS, planet.name, planet.house)
                if meaning:
                    score = self._base_score(meaning.weights, query_type)
                    factors.append(
                        Factor(
                            code=f"{planet.name}_house_{planet.house}",
                            label=f"{planet.name} in house {planet.house}",
                            score=score,
                            topic_scores=meaning.weights,
                            meaning=meaning,
                            context={"kind": "planet_house"},
                        )
                    )
        return factors

    def _aspect_factors(self, aspects: List[Aspect], aspect_origin: str) -> List[Factor]:
        factors: List[Factor] = []
        for asp in aspects:
            meaning = ASPECT_MEANINGS.get(asp.aspect_type)
            if not meaning:
                continue
            # Tight orb means stronger weight
            orb_weight = max(0.2, 1 - (asp.orb / 8.0))
            house_weight = 1.0
            angular = {1, 4, 7, 10}
            if asp.house_a and asp.house_a in angular:
                house_weight += 0.1
            if asp.house_b and asp.house_b in angular:
                house_weight += 0.1
            topic_scores = {k: v * orb_weight for k, v in meaning.weights.items()}
            factors.append(
                Factor(
                    code=f"{aspect_origin}_{asp.planet_a}_{asp.aspect_type}_{asp.planet_b}",
                    label=f"{asp.planet_a} {asp.aspect_type} {asp.planet_b}",
                    score=asp.strength_score * orb_weight * house_weight,
                    topic_scores=topic_scores,
                    meaning=meaning,
                    context={
                        "kind": aspect_origin,
                        "house_a": asp.house_a,
                        "house_b": asp.house_b,
                    },
                )
            )
        return factors

    def _numerology_factors(self, numerology: Dict) -> List[Factor]:
        factors: List[Factor] = []
        for key, data in numerology.items():
            meaning = NUMEROLOGY_MEANINGS.get(key)
            if not meaning:
                continue
            number = data.get("number")
            label = data.get("label", key.replace("_", " ").title())
            topic_scores = meaning.weights
            factors.append(
                Factor(
                    code=f"numerology_{key}",
                    label=f"{label}: {number}",
                    score=self._base_score(topic_scores, "general"),
                    topic_scores=topic_scores,
                    meaning=meaning,
                    context={"kind": "numerology"},
                )
            )
        return factors

    def _aggregate_scores(self, factors: List[Factor]) -> Dict[str, float]:
        scores: Dict[str, float] = {k: 0.0 for k in self.base_weights.keys()}
        for factor in factors:
            for topic, value in factor.topic_scores.items():
                scores[topic] = scores.get(topic, 0.0) + value * factor.score
        return {k: round(v, 3) for k, v in scores.items()}

    def _base_score(self, topic_weights: Dict[str, float], query_type: str) -> float:
        # Very light mapping; can be extended with query-specific emphasis.
        emphasis = {
            "natal_love": {"love": 1.3, "emotional": 1.1},
            "natal_career": {"career": 1.3, "general": 1.05},
            "daily_forecast": {"general": 1.05, "love": 1.05, "career": 1.05},
            "weekly_forecast": {"general": 1.05, "love": 1.05, "career": 1.05},
            "compatibility_romantic": {"love": 1.35, "emotional": 1.1},
            "compatibility_business": {"career": 1.3, "general": 1.1},
        }
        multiplier = emphasis.get(query_type, {})
        # Sum of topic weights drives the base score
        total = sum(topic_weights.values())
        if not total:
            return 0.5
        adj = sum(topic_weights.get(t, 0) * multiplier.get(t, 1.0) for t in topic_weights)
        return round(adj / total, 3)
